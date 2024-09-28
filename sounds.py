import numpy as np
import pygame
import threading
import queue

class SoundSystem:
    def __init__(self):
        self.sample_rate = 44100
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=1024)
        self.sounds = {
            "item_pickup": self.generate_item_pickup_sound(),
            "footstep": self.generate_footstep_sound(),
            "ambient": self.generate_ambient_sound(),
        }
        self.music = {
            "ambient_horror": self.generate_ambient_horror_music(),
        }
        self.current_music = None
        self.music_channel = pygame.mixer.Channel(0)
        self.sound_queue = queue.Queue()
        self.sound_thread = threading.Thread(target=self._sound_worker, daemon=True)
        self.sound_thread.start()

    def generate_sine_wave(self, freq, duration):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        return np.sin(2 * np.pi * freq * t)

    def generate_noise(self, duration):
        return np.random.uniform(-1, 1, int(self.sample_rate * duration))

    def to_stereo(self, mono_audio):
        return np.column_stack((mono_audio, mono_audio))

    def generate_item_pickup_sound(self):
        duration = 0.1
        f = np.linspace(440, 880, int(self.sample_rate * duration), False)
        mono = np.sin(2 * np.pi * f * np.arange(int(self.sample_rate * duration)) / self.sample_rate)
        return self.to_stereo(mono)

    def generate_footstep_sound(self):
        duration = 0.1
        noise = self.generate_noise(duration)
        envelope = np.linspace(1, 0, int(self.sample_rate * duration))
        mono = noise * envelope
        return self.to_stereo(mono)

    def generate_ambient_sound(self):
        duration = 1.0
        noise = self.generate_noise(duration)
        low_freq = self.generate_sine_wave(50, duration)
        mono = (noise * 0.3 + low_freq * 0.7) * 0.5
        return self.to_stereo(mono)

    def generate_ambient_horror_music(self):
        duration = 10.0
        base_freq = 55
        harmonics = [1, 1.5, 2, 2.5, 3]
        waves = [self.generate_sine_wave(base_freq * h, duration) for h in harmonics]
        combined = sum(waves) / len(waves)
        noise = self.generate_noise(duration) * 0.1
        mono = (combined + noise) * 0.5
        return self.to_stereo(mono)

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sound_queue.put(sound_name)

    def _sound_worker(self):
        while True:
            sound_name = self.sound_queue.get()
            if sound_name in self.sounds:
                sound = pygame.sndarray.make_sound((self.sounds[sound_name] * 32767).astype(np.int16))
                sound.play()

    def play_music(self, music_name):
        if music_name in self.music:
            music = pygame.sndarray.make_sound((self.music[music_name] * 32767).astype(np.int16))
            self.music_channel.play(music, loops=-1)

    def stop_music(self):
        self.music_channel.stop()
