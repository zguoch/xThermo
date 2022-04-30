# -*- coding: utf-8 -*-
"""
0. Phase diagram
==============================
"""

# Some python packages for data visualization
import numpy as np 
import time
import copy
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import patches
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
mpl.rcParams['font.family'] = 'Arial'  #default font family
mpl.rcParams['mathtext.fontset'] = 'cm' #font for math
dpi=100
fmt_figs=['pdf'] #['svg','pdf']
result_path='.'
figpath=result_path
def savefig(figname):
    for fmt_fig in fmt_figs:
        figname_full = '%s/%s.%s'%(figpath,figname,fmt_fig)
        plt.savefig(figname_full, bbox_inches='tight')
        print('figure saved: ',figname_full)

# Import package of xThermo
from xThermo import H2O
iaps84 = H2O.cIAPS84()
iapws95_CoolProp = H2O.cIAPWS95_CoolProp()
iapws95 = H2O.cIAPWS95()

# Calculate
def cal_phase(water):
    T = np.linspace(water.Tmin(),water.T_critical(),100)
    p = np.zeros_like(T)
    for i in range(0,len(T)): p[i] = water.Boiling_p(T[i])
    # calculate phase index
    TT, pp = np.meshgrid(np.linspace(0.1,600, 100), np.linspace(1, 400, 100))
    phase = np.zeros_like(TT)
    for i in range(0,TT.shape[0]):
        for j in range(0,TT.shape[1]):
            props=water.UpdateState_TPX(TT[i][j]+273.15, pp[i][j]*1E5)
            phase[i][j]=props.phase
    phase_unique = np.sort(np.unique(phase))
    phase_name = ['']*len(phase_unique)
    for i,phase0 in enumerate(phase_unique): 
        phase[phase==phase0]=i+phase_unique.max()+10
        phase_name[i]=water.phase_name(int(phase0))
    return T,p,TT,pp,phase,phase_name

# Plot both linear and log scale
def phaseDiagram(water, axes=None):
    T,p,TT,pp,phase,phase_name = cal_phase(water)
    if(axes==None): 
        fig,axes=plt.subplots(1,2,figsize=(15,7),gridspec_kw={'wspace':0.02},dpi=dpi)
    
    axes[0].set_ylabel('Pressure (bar)')
    axes[1].set_yscale('log')
    
    # plot
    cmap = plt.get_cmap("Dark2")
    # customize cmap
    colors=list(copy.deepcopy(cmap.colors))
    colors[0:8]=['lightblue','red','lightgreen','lightgray','violet','yellow','lightcyan','lightcyan']
    cmap.colors=tuple(colors)
    for ax in axes:
        ax.set_ylim(pp.min(),pp.max())
        ax.set_xlim(TT.min(),TT.max())
        ax.text(0.98,0.98,water.name(),ha='right',va='top',bbox={'fc':'w','ec':'gray'}, transform=ax.transAxes)
        ax.set_xlabel('Temperature ($^{\circ}$C)')
        ax.plot(T-273.15, p/1E5, label='Boiling curve')
        ax.plot(water.T_critical()-273.15, water.p_critical()/1E5,'o',mfc='r',mec='w',label='Critical point')
        if(ax==axes[0]): 
            CS=ax.contourf(TT,pp,phase, cmap=cmap,vmin=phase.min()-0.5, vmax=phase.max()+0.5, levels=np.linspace(phase.min()-0.5,phase.max()+0.5,len(phase_name)+1))
            ax_cb = ax.inset_axes([0,1.03,2,0.05])
            cb=plt.colorbar(CS, cax=ax_cb, orientation='horizontal',ticklocation='top',ticks=np.arange(phase.min(),phase.max()+1))
            cb.ax.set_xticklabels(phase_name)
        if(ax==axes[1]):
            ax.yaxis.set_ticks_position('right')
            ax.xaxis.set_minor_locator(MultipleLocator(20))
            ax.grid(which='major',color='gray')
            ax.grid(which='minor',color='lightgray')
        ax.legend(loc='lower right')
    savefig('phase_%s'%(water.name()))


# %%
# IAPS84 Phase diagram
# -------------------------
phaseDiagram(iaps84)

# %%
# IAPWS95 Phase diagram: build in xThermo
# --------------------------------------------------
phaseDiagram(iapws95)

# %%
# IAPWS95 Phase diagram: CoolProp
# --------------------------------------------------

phaseDiagram(iapws95_CoolProp)


# %%
# Comparison: saturated properties
# --------------------------------------------------
def cal_props_sat(water, T):
    # T = np.linspace(water.Tmin(),water.T_critical(), 100)
    props={'p':[],'Rho_l':[],'Rho_v':[]}
    for i in range(0,len(T)):
        prop = water.Boiling_p_props(T[i])
        props['p'].append(prop.p)
        props['Rho_l'].append(prop.Rho_l)
        props['Rho_v'].append(prop.Rho_v)
    for key in props.keys(): props[key]=np.array(props[key])
    return props
def plot_comparison():
    T = np.linspace(273.5,iapws95.T_critical(), 100)
    props_84 = cal_props_sat(iaps84,T)
    props_95 = cal_props_sat(iapws95,T)

    fig,axes = plt.subplots(1,2,figsize=(15,7),gridspec_kw={'wspace':0.02})
    # liquid 
    ax = axes[0]
    diff = props_84['p'] - props_95['p']
    ax.plot(T-273.15, diff,marker='.')
    ax.set_ylabel('Saturated pressure (Pa): %s - %s'%(iaps84.name(),iapws95.name()))
    ax.set_xlabel('Temperature ($^{\circ}$C)')

    ax = axes[1]
    diff_l = props_84['Rho_l'] - props_95['Rho_l']
    diff_v = props_84['Rho_v'] - props_95['Rho_v']
    ax.plot(T-273.15, diff_l, label='Liquid',marker='.')
    ax.plot(T-273.15, diff_v, label='Vapor',marker='.')
    ax.legend()
    ax.yaxis.set_ticks_position('right')
    ax.yaxis.set_label_position('right')
    ax.set_ylabel('Saturated density (kg/m^3): %s - %s'%(iaps84.name(),iapws95.name()))
    ax.set_xlabel('Temperature ($^{\circ}$C)')

    savefig('diff_sat')

plot_comparison()