# Kick Chat Bot

A professional, modular, and SOLID-compliant chat bot designed for Kick, written in Python 3.12+ and `asyncio`. 

## Features
- **Async & Fast:** Built entirely on `asyncio` and `aiohttp`.
- **Modular Commands:** Dynamic command discovery. No long `if-elif` chains.
- **Dependency Injection:** Clean decoupling of components for easy testing.
- **Docker Ready:** Minimal, optimized Dockerfile for production deployments.

## Installation

1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scriptsctivate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## .env Oluşturma

Repository içerisindeki `.env.example` dosyasını kopyalayarak `.env` isimli yeni bir dosya oluşturun ve API key'lerinizi girin:
```bash
cp .env.example .env
```

## Çalıştırma

Botu başlatmak için:
```bash
python main.py
```

## Docker ile Çalıştırma

Production veya test ortamında Docker ile çalıştırmak için:
```bash
docker build -t kick-bot .
docker run -d --name kick_bot_instance --env-file .env kick-bot
```

## Yeni Komut Ekleme

Sisteme yeni bir komut eklemek sadece bir dosya oluşturmak kadar kolaydır.
`bot/commands/` dizinine gidin ve `BaseCommand` sınıfından miras alan yeni bir Python dosyası yaratın. Bot başlarken komutunuzu otomatik tanıyacaktır.

## Proje Mimarisi
- `adapters/`: Chat bağlantı katmanı.
- `commands/`: İzole edilmiş komutlar.
- `core/`: Config ve Dependency işlemleri.
- `events/`: Dinamik Command Router.
- `services/`: 3. parti API haberleşmeleri.
