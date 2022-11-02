from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *
from gtts import gTTS #audio
import os
import time #время исполнения
import shutil #удаление всех фацлов папке
from videogrep import videogrep #поиск по видео
import subprocess #для удаления процесса
from icrawler.builtin import GoogleImageCrawler # поимк картинок
#import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize # лишние слова
#nltk.download('stopwords')
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
start_time = time.time()

def text_filter(text_path):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text_path)
    
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
    filtered_sentence = []
    
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    output = ' '.join(map(str, filtered_sentence))
    print('text fo search', output)

    return output

def imagfe_search(filepath, i, textfile):
    new_text = text_filter(textfile)
    print('\n\n\n\t', new_text)
    try_count = 0
    file_name = ''
    while os.path.exists(file_name) == False:
        google_Crawler = GoogleImageCrawler(feeder_threads=6, parser_threads=6, downloader_threads=6,storage = {'root_dir': filepath})
        google_Crawler.crawl(keyword = new_text, max_num = 1, min_size=(1080,1080), max_size=(1920,1920))
        ext = ".jpg"
        

        if os.path.exists(filepath + '000001.png'):
            img = Image.open(filepath + '000001.png')
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img.save(filepath + '000001.jpg')
            img.close()
            os.remove(filepath + '000001.png')

        if i < 10:
            file_name = filepath + '0' + str(i) + ext
            try:
                os.rename(filepath + '000001.jpg', file_name)
                img_resize(file_name)
            except:
                pass
        else:
            file_name = filepath + str(i) + ext
            try:
                os.rename(filepath + '000001.jpg', file_name)
                img_resize(file_name)
            except:
                pass
        try_count += 1
        if try_count == 10:
            break
    

    if os.path.exists(file_name) == False:
        img_gen(filepath, 'resources\\fonts\Times New Roman.ttf', i, textfile)
    img_resize(file_name)
    
def img_resize(filename):
    hight = 1920
    width = 1080
    img = Image.open(filename)
    w, h = img.size
    print(w, h)

    resize = 100 - (width * 100) / w
    new_hight = h - (h * resize / 100)
    new_width = w - (w * resize / 100)
    print(new_width, new_hight)
    new_filename = img.resize((int(new_width), int(new_hight)))
    new_filename.save(filename)

def img_gen(filepath, fnt_path, i, img_text): #надо будет дописать передачу директорий и их нейминга
    width = 1080
    hight = 1920
    
    img_format = '.jpg'
    img_num = i
    if i < 10:
        filename = filepath + '0' + str(img_num) + img_format
    else:
        filename = filepath + str(img_num) + img_format
    text = img_text
  
    new_img = Image.new('RGB', (width, hight), color=(0, 0, 0))

    d = ImageDraw.Draw(new_img)
    fnt_size = 40
    fnt_max_width = 880
   
    fnt = ImageFont.truetype(fnt_path, fnt_size)
    w, h = d.textsize(img_text, font=fnt)
    if w < fnt_max_width:
        while w < fnt_max_width:
            fnt_size += 2
            fnt = ImageFont.truetype(fnt_path, fnt_size)
            w, h = d.textsize(img_text, font=fnt)
    else:
        while w > fnt_max_width:
            fnt_size -= 2
            fnt = ImageFont.truetype(fnt_path, fnt_size)
            w, h = d.textsize(img_text, font=fnt)
    d.multiline_text(((width - w)/2, (hight - h)/2), text, fill=(255,255,255), font = fnt, align = 'center' )
    new_img.save(filename)

def audio_gen(filepath, i, text): # -//-
    ext = '.mp3'
    mytext = text
    language = 'en'
    myobj = gTTS(text=mytext, lang=language, slow=False)
    if i < 10:
        file_name = filepath + '0' + str(i) + ext
    else:
        file_name = filepath + str(i) + ext
    myobj.save(file_name)

def vid_gen(img_filepath, filepath_output, i):
    ext = ".mp4"
    img_ext = ".jpg"
    if i < 10:
        file_name = filepath_output + '0' + str(i) + ext
        img_path = img_filepath + '0' + str(i) + img_ext
    else:
        file_name = filepath_output + str(i) + ext
        img_path = img_filepath + str(i) + img_ext

    video = ImageClip(img_path,duration=0.5)
    video.write_videofile(file_name, fps=12)

def audio_add(audio_filepath, video_filepath, filepath_output,i):
    audio_ext = '.mp3'
    video_ext = '.mp4'
    if i < 10:
        audio_name = audio_filepath + '0' + str(i) + audio_ext
        video_name = video_filepath + '0' + str(i) + video_ext
        output_name = filepath_output + '0' + str(i) + video_ext
    else:
        audio_name = audio_filepath + str(i) + audio_ext
        video_name = video_filepath + str(i) + video_ext
        output_name = filepath_output + str(i) + video_ext

    videoclip = VideoFileClip(video_name)
    audioclip = AudioFileClip(audio_name)

    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    videoclip.write_videofile(output_name)

def vid_compose(video_filepath, filepath_output, output_type, vids_count):
    if is_empty(video_filepath):
        return 'Error'
    clips = []
    for filename in os.listdir(video_filepath):
        if filename.endswith(".mp4"):
            clips.append(VideoFileClip(video_filepath + filename))

    video = concatenate_videoclips(clips, method='compose')
    if output_type == 'none':
        filename = filepath_output + ('episode_') + str(vids_count) + '.mp4'
    #elif output_type == 'intro' or output_type == 'outro':
    else:
        filename = filepath_output + output_type + '.mp4'
    video.write_videofile(filename, threads=6)

def clean_trash():
    shutil.rmtree('tmp_files\\video\\')
    os.mkdir('tmp_files\\video\\')
    shutil.rmtree('tmp_files\\trash_video\\')
    os.mkdir('tmp_files\\trash_video\\')
    shutil.rmtree('tmp_files\img\\')
    os.mkdir('tmp_files\img\\')
    shutil.rmtree('tmp_files\\audio\\')
    os.mkdir('tmp_files\\audio\\')

def is_empty(directory):
    if len(os.listdir(directory + '/') ) == 0:
        return True
    else:    
        print("Directory is not empty")
        return False

def text_sum(i, text, new_vid):
    new_text = ''
    while text[i] != '\n':
        if text[i] == '----\n':
            new_vid = False
            break
        else: 
            new_text += text[i]
            i += 1
    return new_text, i, new_vid

audio_path = 'tmp_files\\audio\\'
img_path = 'tmp_files\img\\'
trash_video_path = 'tmp_files\\trash_video\\'
tmp_video_path = 'tmp_files\\video\\'
const_video_path = 'resources\const_videos\\'
txt_path = 'resources\\txt_files\\'
mtr_path = 'resources\matirials\\'
fnt_path = 'resources\\fonts\Times New Roman.ttf'
final_path = 'output\\'

i = 0 #индекс строки
vids_count = 0 #счетчик готовых эпизодов
count = 0 #кол-во строк в файле
file_name_to_open = txt_path + 'poem.txt' #имя файло из которого считывается текст

clean_trash()

file1 = open(file_name_to_open, 'r', encoding='utf-8')
Lines = file1.readlines()
for line in Lines:
    count += 1
new_vid = True
while i < count:
    while new_vid == True:
        with open(file_name_to_open, 'r', encoding='utf-8') as f:
            text = f.readlines()
            if text[i] == '----\n':
                new_vid = False  
            else:
                if text[i] != '\n':
                    #new_text, i, new_vid = text_sum(i, text, new_vid)
                    #img_gen(img_path, fnt_path, i, new_text)
                    imagfe_search(img_path, i,text[i])
                    audio_gen(audio_path, i, text[i])
                    vid_gen(img_path, tmp_video_path, i)
                    audio_add(audio_path, tmp_video_path, tmp_video_path, i)
            i += 1
            if count <= i:
                break
    #file_to_resize = fragment_search(txt_path, mtr_path, trash_video_path, vids_count)
    #resize_vid(file_to_resize, tmp_video_path, i)
    vid_compose(tmp_video_path, final_path, 'none', vids_count) # можно в название файла вписать слово
    suc_clean = False
    while suc_clean != True:
        try:
            clean_trash()
            suc_clean = True
        except:
            # ffmpeg-win64-v4.2.2.exe
            subprocess.call("taskkill /F /IM ffmpeg-win64-v4.2.2.exe /T")
            print('fail to remove')
            suc_clean = False
            pass
    new_vid = True
    vids_count += 1
    if vids_count == 1:
        break
    
print("--- %s seconds ---" % round(time.time() - start_time))
print('Videos genereted:', vids_count)