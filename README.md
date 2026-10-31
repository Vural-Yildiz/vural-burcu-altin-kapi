# Vural & Burcu — Altın Kapı

Sinematik taş kapı ve mühürlü zarf açılışıyla başlayan, mobil uyumlu dijital davet.

## Çalıştırma

Bu dizini herhangi bir statik web sunucusunda açın. Derleme, kurulum, harici JavaScript kütüphanesi veya API anahtarı gerekmez.

```bash
python3 -m http.server 8000
```

## GitHub Pages

Settings → Pages → Deploy from a branch → `main` / `(root)`.

## Davet bilgileri

`invitation.json` içindeki tarih, saat ve salon alanları, paylaşılan görsellerde bulunmadığı ve Manisa–Salihli daveti için henüz doğrulanmadığı için boştur. Yalnızca doldurulan alanlar gösterilir. Başka bir etkinliğin bilgileri bu davete taşınmamıştır.

## Etkileşimler

- **Daveti aç:** Kullanıcı dokunuşuyla filmi sesli başlatır.
- **Sesi kapat/aç:** Film sesini değiştirir.
- **Davete geç / Escape:** Daveti doğrudan gösterir.
- **Tekrar izle:** Filmi yeniden başlatır.
- **Paylaş:** Desteklenen cihazlarda sistem paylaşımını açar; diğerlerinde bağlantıyı kopyalar. Kendiliğinden mesaj göndermez.
- **Videoyu indir:** Birleştirilmiş davet filmini indirir.
- Hareket azaltma tercihi açık cihazlarda açılış düğmesi doğrudan davete gider; film ayrıca başlatılabilir.

## Varlıklar ve gizlilik

Görseller kullanıcı tarafından sağlanmıştır. Film Runway üzerinden Seedance 2.5 ile, müzik özgün üretim olarak hazırlanmıştır. Kesin konum, telefon, e-posta, izleme betiği, form verisi, gizli anahtar veya süreli imzalı medya adresi içermez. Müzik mevcut bir film müziğinin kopyası değildir.

Statik sayfa video dosyası yüklenmese veya oynatılamasa da daveti gösterir. iOS için `playsinline`, kullanıcı hareketiyle başlatma ve `preload=metadata` kullanılır.
