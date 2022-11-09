import numpy as np
from scipy.constants import pi, m_e, e, c, alpha, hbar
from numba import njit, prange

def get_lw_field(x, y, z, ux, uy, uz, t, n):
    '''
    从坐标和动量计算推迟时间和电场

    x, y, z : ndarray
        坐标向量
    ux, uy, uz : ndarray
        归一化动量，u = p/mc
    t : ndarray
        时间矢量
    n : tuple | list | ndarray
        长度为3的方向矢量
    '''
    t_ret = t - (n[0]*x + n[1]*y + n[2]*z) / c
    inv_gamma = 1 / np.sqrt(ux**2 + uy**2 + uz**2 + 1)
    betax = ux * inv_gamma
    betay = uy * inv_gamma
    betaz = uz * inv_gamma
    # 加速度
    ax = np.concatenate(([0], betax[2:] - betax[:-2], [0]))
    ay = np.concatenate(([0], betay[2:] - betay[:-2], [0]))
    az = np.concatenate(([0], betaz[2:] - betaz[:-2], [0]))

    n_dot_a = n[0]*ax + n[1]*ay + n[2]*az
    n_dot_beta = n[0]*betax + n[1]*betay + n[2]*betaz
    factor = 1 / (1 - n_dot_beta)**3

    Ex = (n_dot_a*(n[0] - betax) + (n_dot_beta - 1) * ax) * factor
    Ey = (n_dot_a*(n[1] - betay) + (n_dot_beta - 1) * ay) * factor
    Ez = (n_dot_a*(n[2] - betaz) + (n_dot_beta - 1) * az) * factor
    return t_ret, Ex, Ey, Ez


@njit(parallel=True)
def get_lw_spectrum(E, t_ret, omega_axis):
    '''
    计算lw谱，不使用FFT直接积分。慢但是方便。

    E : ndarray
        推迟势电场矢量Ex Ey 或Ez
    t_ret : ndarray
        推迟时间矢量
    omega_axis : ndarray
        频谱的频率轴
    '''
    nomega = len(omega_axis)
    E_ft = np.zeros_like(omega_axis, dtype=np.complex128)
    
    # definition of Fourier transformation
    for i in prange(nomega):
        w = omega_axis[i]
        # trapzoid integral
        E_ft[i] = np.trapz(E * np.exp(-1j*w*t_ret), t_ret) 

    # normalize
    return E_ft / np.sqrt(2*pi)