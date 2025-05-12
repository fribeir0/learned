import yt_dlp

def listar_videos_do_canal(url_canal):
    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'quiet': True,
        'force_generic_extractor': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url_canal, download=False)
        if 'entries' in info:
            urls = [video['url'] for video in info['entries']]
            return ['https://www.youtube.com/watch?v=' + video_id for video_id in urls]
        else:
            return []

# Exemplo de uso:
canal_url = 'https://www.youtube.com/@razukbackstage/videos'
links = listar_videos_do_canal(canal_url)
for link in links:
    print(link)
