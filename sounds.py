import numpy as np
import pygame
import threading
import queue
import random
import scipy.signal

class SoundSystem:
    def __init__(self):
        self.enabled = True  # New variable to control sound system
        self.sample_rate = 44100
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=1024)
        self.sounds = {
            "item_pickup": self.generate_item_pickup_sound(),
            "footstep": self.generate_footstep_sound(),
            "ambient": self.generate_ambient_sound(),
            "typing": self.generate_typing_sound(),
            "echo": self.generate_echo_sound(),
        }
        self.music = {
            "ambient_horror": self.generate_ambient_horror_music(),
        }
        self.current_music = None
        self.music_channel = pygame.mixer.Channel(0)
        self.ambient_channel = pygame.mixer.Channel(1)
        self.sound_queue = queue.Queue()
        self.sound_thread = threading.Thread(target=self._sound_worker, daemon=True)
        self.sound_thread.start()
        self.signal_strength = 100
        self.ambient_sounds = self.generate_ambient_sounds()
        self.ambient_timer = 0

    def generate_sine_wave(self, freq, duration):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        return np.sin(2 * np.pi * freq * t)

    def generate_noise(self, duration):
        return np.random.uniform(-1, 1, int(self.sample_rate * duration))

    def to_stereo(self, mono_audio):
        return np.column_stack((mono_audio, mono_audio))

    def generate_item_pickup_sound(self):
        duration = 0.1
        beep_freq = 1000  # A 1kHz beep, typical for old computer systems
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        mono = np.sin(2 * np.pi * beep_freq * t)
        # Apply a simple envelope to avoid clicks
        envelope = np.concatenate([np.linspace(0, 1, int(self.sample_rate * 0.01)), 
                                   np.ones(int(self.sample_rate * 0.08)), 
                                   np.linspace(1, 0, int(self.sample_rate * 0.01))])
        mono = mono * envelope
        return self.to_stereo(mono)

    def generate_footstep_sound(self):
        duration = 0.2
        # Generate a low frequency rumble
        rumble_freq = 30  # 30 Hz for a deep, low sound
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        rumble = np.sin(2 * np.pi * rumble_freq * t)
        
        # Generate some mechanical noise
        noise = self.generate_noise(duration) * 0.3
        
        # Combine rumble and noise
        mono = rumble * 0.7 + noise
        
        # Apply an envelope to shape the sound
        envelope = np.concatenate([
            np.linspace(0, 1, int(self.sample_rate * 0.05)),  # Attack
            np.ones(int(self.sample_rate * 0.1)),             # Sustain
            np.linspace(1, 0, int(self.sample_rate * 0.05))   # Release
        ])
        
        mono = mono * envelope
        return self.to_stereo(mono * 0.25)  # Reduce volume by half

    def generate_ambient_sound(self):
        duration = 1.0
        noise = self.generate_noise(duration)
        low_freq = self.generate_sine_wave(50, duration)
        mono = (noise * 0.3 + low_freq * 0.7) * 0.5
        return self.to_stereo(mono)

    def generate_ambient_horror_music(self):
        duration = 16.0
        base_freq = 77.78
        harmonics = [1, 1.5, 2, 2.5, 3]
        waves = [self.generate_sine_wave(base_freq * h, duration) for h in harmonics]
        combined = sum(waves) / len(waves)
        noise = self.generate_noise(duration) * 0.1
        
        # Add low melody and harmony
        low_notes = [77.78, 87.31, 103.83, 116.54, 138.59]  # D2, F2, G#2, A#2, C3
        high_notes = [77.78, 87.31, 103.83, 116.54, 138.59]  # D2, F2, G#2, A#2, C3
        #high_notes = [155.56, 174.61, 207.65, 233.08, 277.18, 349.23]  # D3, F3, G#3, A#3, C4, F4
        low_melody = np.zeros(int(self.sample_rate * duration))
        high_melody = np.zeros(int(self.sample_rate * duration))
        note_duration = 4.0  # Shorter duration to fit more notes

        for i in range(0, int(duration), int(note_duration)):
            low_note = random.choice(low_notes)
            high_note = random.choice(high_notes)
            # Check if notes are equal or adjacent in the list
            if low_note == high_note or abs(low_notes.index(low_note) - high_notes.index(high_note)) <= 1:
                # If so, choose only one note
                chosen_note = random.choice([low_note, high_note])
                low_note = high_note = chosen_note
            # Introduce very small detuning for both notes
            detune_factor_low = random.uniform(0.95, 1.05)  # ±5% detuning
            detune_factor_high = random.uniform(0.95, 1.05)  # ±5% detuning
            low_note *= detune_factor_low
            high_note *= detune_factor_high
            tempo_low = random.choice([1, 0.5])  # 1/1 or 1/2 tempo for low notes
            tempo_high = random.choice([1, 0.5, 0.25])  # 1/1 or 1/2 or 1/4 tempo for high notes
            
            t_low = np.linspace(0, note_duration * tempo_low, int(self.sample_rate * note_duration * tempo_low), False)
            t_high = np.linspace(0, note_duration * tempo_high, int(self.sample_rate * note_duration * tempo_high), False)
            
            low_wave = np.sin(2 * np.pi * low_note * t_low)
            high_wave = np.sin(2 * np.pi * high_note * t_high)
            
            start_low = int(i * self.sample_rate)
            end_low = start_low + len(low_wave)
            if end_low > len(low_melody):
                end_low = len(low_melody)
                low_wave = low_wave[:end_low-start_low]
            low_melody[start_low:end_low] += low_wave

            start_high = int(i * self.sample_rate)
            end_high = start_high + len(high_wave)
            if end_high > len(high_melody):
                end_high = len(high_melody)
                high_wave = high_wave[:end_high-start_high]
            high_melody[start_high:end_high] += high_wave

        # Normalize and combine melodies
        low_melody = low_melody / np.max(np.abs(low_melody))
        high_melody = high_melody / np.max(np.abs(high_melody))
        melody = (low_melody + high_melody) / 2
        
        melody = melody / np.max(np.abs(melody))  # Normalize
        mono = (combined * 0.35 + noise * 0.35 + melody * 0.3) * 0.5
        return self.to_stereo(mono)

    def generate_distortion_sound(self):
        duration = random.uniform(0.05, 0.2)
        noise = self.generate_noise(duration)
        crackle = np.random.choice([-1, 0, 1], size=int(self.sample_rate * duration), p=[0.05, 0.9, 0.05])
        hum = self.generate_sine_wave(50, duration) * 0.1
        combined = (noise * 0.3 + crackle * 0.5 + hum * 0.2) * 0.5
        return self.to_stereo(combined)

    def update_distortion(self, signal_strength):
        if not self.enabled:
            return
        self.distortion_intensity = min(1,max(0, 1 - (signal_strength**1.05 / 100)))
        if self.distortion_intensity > 0:
            if not self.distortion_channel.get_busy():
                distortion = pygame.sndarray.make_sound((self.distortion_sound * 32767 * self.distortion_intensity).astype(np.int16))
                self.distortion_channel.play(distortion, loops=-1)
            self.distortion_channel.set_volume(self.distortion_intensity)
        else:
            self.distortion_channel.stop()

    def apply_distortion_to_sound(self, sound):
        if not self.enabled:
            return sound
        if self.distortion_intensity > 0:
            noise = self.generate_noise(len(sound) / self.sample_rate) * self.distortion_intensity * 0.3
            distorted_sound = sound + noise[:, np.newaxis]
            return np.clip(distorted_sound, -1, 1)
        return sound

    def play_sound(self, sound_name):
        if not self.enabled:
            return
        if sound_name in self.sounds:
            self.sound_queue.put(sound_name)

    def _sound_worker(self):
        while True:
            sound_info = self.sound_queue.get()
            if not self.enabled:
                continue
            if isinstance(sound_info, tuple):
                sound_name, pygame_sound = sound_info
                pygame_sound.play()
            else:
                sound_name = sound_info
                if sound_name in self.sounds:
                    sound = self.sounds[sound_name]
                    pygame_sound = pygame.sndarray.make_sound((sound * 32767).astype(np.int16))
                    pygame_sound.play()

    def play_music(self, music_name):
        if not self.enabled:
            return
        if music_name in self.music:
            music = self.music[music_name]
            pygame_music = pygame.sndarray.make_sound((music * 32767).astype(np.int16))
            self.music_channel.play(pygame_music, loops=-1)

    def stop_music(self):
        if not self.enabled:
            return
        self.music_channel.stop()

    def generate_typing_sound(self):
        duration = 0.05
        # Generate a lower frequency base sound
        base_freq = 100  # Lower frequency for a more natural sound
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        base_sound = np.sin(2 * np.pi * base_freq * t)
        
        # Add some soft noise for texture
        noise = self.generate_noise(duration) * 0.1
        
        # Combine base sound and noise
        combined = base_sound + noise
        
        # Apply an envelope to shape the sound
        envelope = np.exp(-t * 20)  # Exponential decay for a more natural fade-out
        
        mono = combined * envelope * 0.4  # Reduced volume
        return self.to_stereo(mono)

    def generate_ambient_sounds(self):
        sounds = []
        for _ in range(15):  # Generate 15 different ambient sounds
            duration = random.uniform(0.15, 0.5)
            freq = random.uniform(100, 500)
            noise = self.generate_noise(duration) * 0.3
            tone = self.generate_sine_wave(freq, duration) * 0.2
            sound = self.to_stereo(noise + tone)
            sounds.append(pygame.sndarray.make_sound((sound * 32767).astype(np.int16)))
        return sounds

    def update_ambient_sounds(self, delta_time):
        if not self.enabled:
            return
        self.ambient_timer += delta_time
        if self.ambient_timer >= self.get_ambient_interval():
            self.ambient_timer = 0
            self.play_random_ambient_sound()

    def get_ambient_interval(self):
        # Interval decreases as signal strength decreases
        return min(5, max(0.05, 2 * (self.signal_strength**0.7 / 100)))

    def play_random_ambient_sound(self):
        if not self.enabled:
            return
        if random.random() < 1 - (self.signal_strength / 100):
            sound = random.choice(self.ambient_sounds)
            self.ambient_channel.play(sound)

    def update_signal_strength(self, signal_strength):
        if not self.enabled:
            return
        self.signal_strength = signal_strength
        # Adjust the volume of the background noise
        noise_volume = 1 - (signal_strength / 100)
        self.ambient_channel.set_volume(noise_volume * 0.5)  # Max volume of 0.5 for ambient sounds

    def generate_echo_sound(self):
        duration = random.uniform(7.0, 9.0)  # Variable duration for unpredictability
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Generate a base for the unsettling sound
        base_freq = random.uniform(40, 50)  # Random base frequency for variability
        pitch_curve = np.cumsum(np.random.normal(0, 0.5, len(t)))  # Natural, random pitch curve
        pitch_curve = pitch_curve / np.max(np.abs(pitch_curve)) * 20  # Normalize and scale
        base_sound = 0.7 * np.tanh(np.sin(2 * np.pi * (base_freq + pitch_curve) * t))  # Use tanh for soft clipping
        
        # Add a distorted, low-pitched scream/moo component with slow vibrato
        scream_freq = random.uniform(50, 60)
        scream_mod = 60 * np.cumsum(np.random.normal(0, 0.3, len(t)))  # Another random curve
        scream_mod = scream_mod / np.max(np.abs(scream_mod))
        vibrato_rate = random.uniform(0.7, 1.2)  # Hz, adjust for desired vibrato speed
        vibrato_depth = random.uniform(1.5, 2.5)  # Hz, adjust for desired vibrato intensity
        vibrato = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        scream = 0.5 * np.tanh(np.sin(2 * np.pi * (scream_freq + scream_mod + vibrato) * t))
        
        # Add a deep, rumbling component
        rumble_freq = random.uniform(20, 30)
        rumble = 0.6 * np.tanh(np.sin(2 * np.pi * rumble_freq * t))
        
        # Combine all components with some randomness
        sound = base_sound + scream + rumble
        #sound += 0.2 * self.generate_noise(duration)  # Add some noise for texture
        
        # Apply a more natural, asymmetric envelope
        attack = np.linspace(0, 1, int(self.sample_rate * 1.0))  # Longer attack for 7-9 second duration
        decay = np.exp(-np.linspace(0, 3, int(self.sample_rate * (duration - 1.0))))  # Adjusted decay
        envelope = np.concatenate([attack, decay])[:len(sound)]
        sound *= envelope
        
        # Add some random distortions
        distortion_points = np.random.randint(0, len(sound), 50)  # Increased number of distortion points
        sound[distortion_points] *= np.random.uniform(0.5, 1.5, 50)
        
        # Normalize
        sound = sound / np.max(np.abs(sound))
        
        # Apply low-pass filter2
        cutoff_freq = 550 + random.uniform(-40, 40)  # Adjust this value to change the filter's cutoff frequency
        b, a = scipy.signal.butter(6, cutoff_freq / (self.sample_rate / 2), btype='low', analog=False)
        filtered_sound = scipy.signal.lfilter(b, a, sound)
        
        # Adjust volume and convert to stereo
        return self.to_stereo(filtered_sound * random.uniform(0.7, 0.7))  # Randomize final volume slightly

    def play_echo(self, direction, distance):
        if not self.enabled:
            return
        if "echo" in self.sounds:
            sound = self.sounds["echo"].copy()
            
            # Adjust volume based on distance
            volume = max(0, 1 - (distance / 50))  # Assume max distance is 50
            sound *= volume
            
            # Adjust stereo based on direction
            if direction < 0:  # Source is to the left
                sound[:, 1] *= max(0, 1 + direction)  # Reduce right channel
            elif direction > 0:  # Source is to the right
                sound[:, 0] *= max(0, 1 - direction)  # Reduce left channel
            
            pygame_sound = pygame.sndarray.make_sound((sound * 32767).astype(np.int16))
            self.sound_queue.put(("echo", pygame_sound))
2