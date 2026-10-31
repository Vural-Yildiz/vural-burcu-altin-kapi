#!/usr/bin/env python3
"""Rebuild the 720x1280 invitation from accepted Runway footage at 1x speed."""
from pathlib import Path
from fractions import Fraction
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
WORK = ROOT / 'work'
PUBLIC = ROOT / 'dist' if (ROOT / 'dist').is_dir() else ROOT
OUT = PUBLIC / 'assets' / 'film.mp4'
W, H = 720, 1280


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def ffmpeg(args):
    result = subprocess.run(['ffmpeg', '-nostdin', '-y', '-v', 'error', *map(str, args)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)


def make_title():
    # One precise typographic overlay; footage remains full-frame and unwarped.
    layer = np.zeros((H, W, 4), dtype=np.uint8)
    for y in range(300):
        layer[y, :, :3] = (3, 8, 12)
        layer[y, :, 3] = int(190 * (1 - y / 300) ** 1.6)
    im = Image.fromarray(layer)
    draw = ImageDraw.Draw(im)
    serif = '/usr/share/fonts/opentype/urw-base35/P052-Roman.otf'
    sans = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    title_font = ImageFont.truetype(serif, 52)
    location_font = ImageFont.truetype(sans, 15)
    def centered(text, y, font, fill):
        box = draw.textbbox((0, 0), text, font=font)
        draw.text(((W - (box[2] - box[0])) / 2 - box[0], y - box[1]), text, font=font, fill=fill)
    centered('Vural & Burcu', 91, title_font, '#f6e6bf')
    centered('M A N İ S A   ·   S A L İ H L İ', 162, location_font, '#e2c18a')
    title_path = WORK / 'title-overlay.png'
    im.save(title_path)
    return title_path


def main():
    sources = [WORK / 'gate.mp4', WORK / 'envelope.mp4']
    metadata = [probe(p) for p in sources]
    vstreams = [next(s for s in m['streams'] if s['codec_type'] == 'video') for m in metadata]
    for p, m in zip(sources, metadata):
        if not any(s['codec_type'] == 'audio' for s in m['streams']):
            raise RuntimeError(f'Missing natural-sound stem: {p.name}')
    fps = Fraction(vstreams[0]['avg_frame_rate'])
    durations = [float(s.get('duration') or m['format']['duration']) for s, m in zip(vstreams, metadata)]
    frame_counts = [round(d * fps) for d in durations]
    durations = [n / fps for n in frame_counts]
    total = float(sum(durations))
    title = make_title()
    fade_start = total - 4.0
    graphs = []
    for i, duration in enumerate(durations):
        d = float(duration)
        graphs.append(f'[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps},setpts=PTS-STARTPTS[v{i}]')
        graphs.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={d:.8f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.12,afade=t=out:st={d-.15:.8f}:d=0.15,volume=0.60[a{i}]')
    graphs += [
        '[v0][a0][v1][a1]concat=n=2:v=1:a=1[picture][natural]',
        f'[3:v]format=rgba,fade=t=in:st={fade_start:.8f}:d=0.65:alpha=1[title]',
        '[picture][title]overlay=0:0:eof_action=pass:shortest=1[video]',
        f'[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={total:.8f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.2,afade=t=out:st={total-2:.8f}:d=2,volume=0.34[music]',
        '[natural][music]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=10[audio]',
    ]
    args = ['-i', sources[0], '-i', sources[1], '-i', WORK/'music.mp3', '-loop', '1', '-framerate', str(fps), '-i', title,
            '-filter_complex', ';'.join(graphs), '-map', '[video]', '-map', '[audio]',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
            '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', OUT]
    ffmpeg(args)
    manifest = {
        'output': str(OUT.relative_to(ROOT)), 'width': W, 'height': H,
        'frame_rate': str(fps), 'actual_picture_duration_seconds': total,
        'playback_speed': 1.0, 'join': 'hard match cut at the same open doorway',
        'art_direction': 'Photographic charcoal stone and restrained warm gold; classical serif names; rigid geometry; natural sound with original instrumental score.',
        'timeline': [
            {'asset_id': 'gate', 'source': 'work/gate.mp4', 'source_in': 0, 'source_out': float(durations[0]), 'sequence_start': 0, 'sequence_end': float(durations[0]), 'audio_owner': 'natural sound'},
            {'asset_id': 'envelope', 'source': 'work/envelope.mp4', 'source_in': 0, 'source_out': float(durations[1]), 'sequence_start': float(durations[0]), 'sequence_end': total, 'audio_owner': 'natural sound'},
            {'asset_id': 'title', 'source': 'work/title-overlay.png', 'sequence_start': fade_start, 'settled': fade_start+.65, 'sequence_end': total},
            {'asset_id': 'music', 'source': 'work/music.mp3', 'source_in': 0, 'source_out': total, 'sequence_start': 0, 'sequence_end': total},
        ],
        'provenance': {
            'reference_images': 'User-supplied photographs/illustrations, retained unmodified in dist/assets.',
            'gate_runway_task': '4909ef91-be0b-48b3-b907-41cd35da27f3',
            'envelope_runway_task': 'b58a5426-9b98-4b72-8ade-acf8643ed414',
            'music_runway_task': '8c82f6fe-f907-459e-8260-78a51499ffeb',
            'retrieval': 'Retrieve source media from these task IDs in the owner’s connected Runway workspace, or use the source media included in the working project. No signed URLs or credentials are stored.',
        },
        'source_metadata': metadata,
        'final_metadata': probe(OUT),
    }
    (ROOT/'timeline.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps({'output': str(OUT), 'duration': total, 'bytes': OUT.stat().st_size}))


if __name__ == '__main__':
    main()
