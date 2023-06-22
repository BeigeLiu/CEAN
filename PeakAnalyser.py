import numpy as np
from scipy.interpolate import interp1d
def CalculateCharge(data,peak_index,signal_type):
    ##### function to calculate the total charge of the signal
    if signal_type == 0:
        return 0,0,0
    elif signal_type == 1:
        begin = max(int(peak_index - 300),0)
        end   = min(int(peak_index + 300),data.shape[0])
        voltages = data[begin:end]
        time     = np.linspace(0,voltages.shape[0]*1e-9*4,voltages.shape[0])
        interp_func = interp1d(time,voltages)
        t_interp    = np.linspace(0,voltages.shape[0]*1e-9*4,voltages.shape[0]*100)
        v_interp    = interp_func(t_interp)
        ids         = np.where(v_interp>0.1*(np.max(v_interp)))[0]
        charge      = np.sum(v_interp[ids[0]:ids[-1]])*1e-9*4/100/50
    elif signal_type == 2:
        begin = max(int(peak_index - 20),0)
        end   = min(int(peak_index + 20),data.shape[0])
        voltages = data[begin:end]
        time  = np.linspace(0,voltages.shape[0]*1e-9*4,voltages.shape[0])
        interp_func = interp1d(time,voltages)
        t_interp    = np.linspace(0,voltages.shape[0]*1e-9*4,voltages.shape[0]*100)
        v_interp    = interp_func(t_interp)
        ids         = np.where(v_interp>0.1*(np.max(v_interp)))[0]
        charge      = np.sum(v_interp[ids[0]:ids[-1]])*1e-9*4/100/50
    else:
        print('Signal Type Must be 0,1 or 2')
        raise ValueError 
    return charge,ids[0]/100+begin,ids[-1]/100+begin

