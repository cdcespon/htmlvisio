import wave
import struct
import math

SAMPLE_RATE = 44100

def generate_ambient_track(filename, duration_sec=88):
    num_samples = int(SAMPLE_RATE * duration_sec)
    
    # Define chord progression with timestamps and frequencies
    chords = [
        # (start_s, end_s, [frequencies in Hz], arpeggio_notes)
        (0,  12, [130.81, 196.00, 246.94, 329.63], [523.25, 659.25, 783.99]),        # Cmaj7
        (12, 24, [110.00, 164.81, 196.00, 261.63, 329.63], [440.00, 523.25, 659.25]), # Am9
        (24, 36, [87.31,  130.81, 174.61, 220.00, 329.63], [349.23, 440.00, 523.25]), # Fmaj7
        (36, 48, [98.00,  146.83, 174.61, 261.63, 293.66], [392.00, 523.25, 587.33]), # G7sus4
        (48, 60, [82.41,  123.47, 164.81, 196.00, 293.66], [329.63, 392.00, 587.33]), # Em7
        (60, 72, [87.31,  130.81, 174.61, 220.00, 261.63], [349.23, 440.00, 523.25]), # Fadd9
        (72, 88, [130.81, 196.00, 246.94, 293.66, 329.63], [523.25, 587.33, 659.25]), # Cmaj9
    ]
    
    data = bytearray()
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        
        # Determine active chord
        left_val = 0.0
        right_val = 0.0
        
        # Global fade-in (2s) and fade-out (3s)
        global_env = 1.0
        if t < 2.5:
            global_env = t / 2.5
        elif t > duration_sec - 3.5:
            global_env = max(0.0, (duration_sec - t) / 3.5)
            
        for c_start, c_end, pad_notes, arp_notes in chords:
            # Overlap slightly for smooth crossfade
            cross_time = 1.5
            if c_start - cross_time <= t <= c_end + cross_time:
                # Envelope for this chord
                chord_t = t - c_start
                chord_len = c_end - c_start
                
                # Attack and release of the chord
                if chord_t < 1.2:
                    chord_env = max(0.0, (t - (c_start - cross_time)) / (1.2 + cross_time))
                elif chord_t > chord_len:
                    chord_env = max(0.0, 1.0 - (chord_t - chord_len) / cross_time)
                else:
                    chord_env = 1.0
                
                # Warm Pad notes
                for idx, freq in enumerate(pad_notes):
                    pan = (idx / (len(pad_notes) - 1)) * 0.6 + 0.2 if len(pad_notes) > 1 else 0.5
                    
                    # Subtle detune chorus
                    detune = math.sin(2 * math.pi * 0.25 * t + idx) * 0.6
                    f = freq + detune
                    
                    # Fundamental + soft harmonics
                    w1 = math.sin(2 * math.pi * f * t)
                    w2 = 0.35 * math.sin(4 * math.pi * f * t)
                    w3 = 0.12 * math.sin(6 * math.pi * f * t)
                    note_sample = (w1 + w2 + w3) * 0.08 * chord_env
                    
                    left_val += note_sample * (1.0 - pan)
                    right_val += note_sample * pan
                
                # Gentle high-register bell arpeggio every 2 seconds
                arp_period = 2.4
                arp_sub_t = chord_t % arp_period
                arp_idx = int((chord_t / 0.8) % len(arp_notes))
                arp_freq = arp_notes[arp_idx]
                
                # Pluck envelope: sharp attack, exponential decay
                bell_env = math.exp(-arp_sub_t * 3.5) * 0.06 * chord_env
                if bell_env > 0.001:
                    bell_w = (math.sin(2 * math.pi * arp_freq * t) + 
                              0.3 * math.sin(4 * math.pi * arp_freq * t)) * bell_env
                    left_val += bell_w * 0.4
                    right_val += bell_w * 0.6
        
        # Master volume and clamp
        left_final = max(-0.95, min(0.95, left_val * global_env))
        right_final = max(-0.95, min(0.95, right_val * global_env))
        
        # Convert to 16-bit PCM
        left_int = int(left_final * 32767)
        right_int = int(right_final * 32767)
        
        data += struct.pack('<hh', left_int, right_int)
    
    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(data)
        
    print(f"Generated soft ambient background track: {filename} ({duration_sec}s)")

if __name__ == '__main__':
    generate_ambient_track('ambient_soft_music.wav', 88)
