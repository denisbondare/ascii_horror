import numpy as np
import pygame
import threading
import queue
import random

class SoundSystem:
    def __init__(self):
        self.sample_rate = 44100
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=1024)
        self.sounds = {
            "item_pickup": self.generate_item_pickup_sound(),
            "footstep": self.generate_footstep_sound(),
            "ambient": self.generate_ambient_sound(),
            "typing": self.generate_typing_sound(),
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

    def generate_distortion_sound(self):
        duration = 1.0
        noise = self.generate_noise(duration)
        crackle = np.random.choice([-1, 0, 1], size=int(self.sample_rate * duration), p=[0.05, 0.9, 0.05])
        hum = self.generate_sine_wave(50, duration) * 0.1
        combined = (noise * 0.3 + crackle * 0.5 + hum * 0.2) * 0.5
        return self.to_stereo(combined)

    def update_distortion(self, signal_strength):
        self.distortion_intensity = max(0, 1 - (signal_strength / 100))
        if self.distortion_intensity > 0:
            if not self.distortion_channel.get_busy():
                distortion = pygame.sndarray.make_sound((self.distortion_sound * 32767 * self.distortion_intensity).astype(np.int16))
                self.distortion_channel.play(distortion, loops=-1)
            self.distortion_channel.set_volume(self.distortion_intensity)
        else:
            self.distortion_channel.stop()

    def apply_distortion_to_sound(self, sound):
        if self.distortion_intensity > 0:
            noise = self.generate_noise(len(sound) / self.sample_rate) * self.distortion_intensity * 0.3
            distorted_sound = sound + noise[:, np.newaxis]
            return np.clip(distorted_sound, -1, 1)
        return sound

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sound_queue.put(sound_name)

    def _sound_worker(self):
        while True:
            sound_name = self.sound_queue.get()
            if sound_name in self.sounds:
                sound = self.sounds[sound_name]
                pygame_sound = pygame.sndarray.make_sound((sound * 32767).astype(np.int16))
                pygame_sound.play()

    def play_music(self, music_name):
        if music_name in self.music:
            music = self.music[music_name]
            pygame_music = pygame.sndarray.make_sound((music * 32767).astype(np.int16))
            self.music_channel.play(pygame_music, loops=-1)

    def stop_music(self):
        self.music_channel.stop()

    def generate_typing_sound(self):
        duration = 0.05
        noise = self.generate_noise(duration)
        envelope = np.linspace(1, 0, int(self.sample_rate * duration))
        mono = noise * envelope * 0.3
        return self.to_stereo(mono)

    def generate_ambient_sounds(self):
        sounds = []
        for _ in range(5):  # Generate 5 different ambient sounds
            duration = random.uniform(0.2, 0.5)
            freq = random.uniform(100, 500)
            noise = self.generate_noise(duration) * 0.3
            tone = self.generate_sine_wave(freq, duration) * 0.2
            sound = self.to_stereo(noise + tone)
            sounds.append(pygame.sndarray.make_sound((sound * 32767).astype(np.int16)))
        return sounds

    def update_ambient_sounds(self, delta_time):
        self.ambient_timer += delta_time
        if self.ambient_timer >= self.get_ambient_interval():
            self.ambient_timer = 0
            self.play_random_ambient_sound()

    def get_ambient_interval(self):
        # Interval decreases as signal strength decreases
        return max(0.5, 5 * (self.signal_strength / 100))

    def play_random_ambient_sound(self):
        if random.random() < 1 - (self.signal_strength / 100):
            sound = random.choice(self.ambient_sounds)
            self.ambient_channel.play(sound)

    def update_signal_strength(self, signal_strength):
        self.signal_strength = signal_strength
        # Adjust the volume of the background noise
        noise_volume = 1 - (signal_strength / 100)
        self.ambient_channel.set_volume(noise_volume * 0.5)  # Max volume of 0.5 for ambient sounds
