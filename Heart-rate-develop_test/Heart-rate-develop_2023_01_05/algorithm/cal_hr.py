import cv2
import math


class cal_hr:
    def __init__(self, data_len, fps, low, high):
        self.m_length = data_len
        self.fps = fps
        self.low = low
        self.high = high
        self.hr = 0
        self.v_time_index = 0
        self.v_time = [1000.0 / fps] * self.m_length

    def update_v_time(self, dis_time):
        self.v_time[self.v_time_index] = dis_time
        self.v_time_index = (self.v_time_index + 1) % self.m_length

    def calculate(self, data):
        v_dftmat = cv2.dft(data)
        v_FA = [0] * int(self.m_length / 2 + 1)
        v_FA[0] = v_dftmat[0] * v_dftmat[0]
        if self.m_length % 2 == 0:
            for i in range(1, int(self.m_length / 2)):
                v_FA[i] = (v_dftmat[2 * i - 1] * v_dftmat[2 * i - 1])[0] + (v_dftmat[2 * i] * v_dftmat[2 * i])[0]
            v_FA[-1] = v_dftmat[-1] * v_dftmat[-1]
        else:
            for i in range(1, int(self.m_length / 2)):
                v_FA[i] = (v_dftmat[2 * i - 1] * v_dftmat[2 * i - 1])[0] + (v_dftmat[2 * i] * v_dftmat[2 * i])[0]

        # time = 1000.0/self.fps * self.m_length
        time = 0.0
        for i in range(self.m_length):
            time += self.v_time[i]

        bottom = (int)(self.low * time / 1000.0)
        top = (int)(self.high * time / 1000.0)

        maxpower = 0.0
        i_maxpower = 0
        for i in range(bottom + 2, top - 1):
            if maxpower < v_FA[i]:
                maxpower = v_FA[i]
                i_maxpower = i

        noise_power = 0.0
        signal_power = 0.0
        signal_moment = 0.0
        for i in range(bottom, top + 1):
            if i >= (i_maxpower - 2) and (i < i_maxpower + 2):
                signal_power += v_FA[i]
                signal_moment += i * v_FA[i]
            else:
                noise_power += v_FA[i]

        snr = 0.0
        if signal_power > 0.01 and noise_power > 0.01:
            snr = 10.0 * math.log10(signal_power / noise_power) + 1
            bias = i_maxpower - signal_moment / signal_power
            snr *= 1.0 / (1.0 + bias * bias)

        # 如果snr一直比较低，没有办法测试，可以将if判断直接注释，即时获取心率
        if snr > 0.5:
            self.hr = signal_moment / signal_power * 60000 / time

        return self.hr, snr
