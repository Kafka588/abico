from f5_tts.api import F5TTS

def test_tts():
    # Use paths from your working F5-TTS project
    model_path = "C:/Users/huree/Documents/f5tts/F5-TTS/ckpts/mongolian_multi/model_226800.pt"
    vocab_path = "C:/Users/huree/Documents/f5tts/F5-TTS/data/mongolian_multi_pinyin/vocab.txt"
    ref_audio_path = "C:/Users/huree/Documents/f5tts/F5-TTS/speaker_353_segment_228.wav"
    output_path = "test_output.wav"
    
    print("Initializing TTS...")
    tts = F5TTS(
        model_type="F5-TTS",
        ckpt_file=model_path,
        vocab_file=vocab_path,
        use_ema=True
    )
    
    test_text = "Лаборатори сургуулиудтай гурван жилийн өмнөөс гэрээ байгуулснаар манай сурлагын амжилт эрс сайжирсанд баяртай байгаа."
    
    print("\nGenerating speech...")
    tts.infer(
        gen_text=test_text.lower().strip(),
        ref_text=test_text.lower().strip(),
        ref_file=ref_audio_path,
        nfe_step=32,
        file_wave=output_path,
        speed=1.0
    )

if __name__ == "__main__":
    test_tts()