# -*- coding: utf-8 -*-
"""
1. Critical curve
=========================
.. include:: /include.rst_
Calculate critical curve of H2O-NaCl system based on IAPS84 and IAPWS95 EOS,
and compare result with :cite:`Driesner2007Part2`.
"""

# %%
# Key code snippet
# --------------------------------
#
# .. code:: python
#
#     import numpy as np
#     from xThermo import H2O
#     from xThermo import H2ONaCl
#     sw = H2ONaCl.cH2ONaCl("IAPS84") #IAPS84, IAPWS95
#     T=np.linspace(sw.Tmin(), sw.Tmax(), 200) # Temperature array
#     P,X=np.array(sw.P_X_Critical(T)) # calculate critical pressure and composition for given temperature
# .. seealso::
#
#     The C++ member function |P_X_Critical| and python wrapper function :py:meth:`xThermo.H2ONaCl.cH2ONaCl.P_X_Critical`.

import numpy as np
import time
import linecache
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import patches
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
from tabulate import tabulate
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
# 3d plot
import helpfunc
mpl.rcParams['font.family'] = 'Arial'  # default font family
mpl.rcParams['mathtext.fontset'] = 'cm'  # font for math
fmt_figs = ['pdf']  # ['svg','pdf']
figpath = '.'
result_path='../../../gallery_H2ONaCl/pT'
def savefig(figname):
    for fmt_fig in fmt_figs:
        figname_full = '%s/%s.%s' % (figpath, figname, fmt_fig)
        plt.savefig(figname_full, bbox_inches='tight')
        print('figure saved: ', figname_full)
compare = lambda a,b : float(str('%.6e'%(a)))-float(str('%.6e'%(b)))
# Import package of xThermo
from xThermo import H2O
from xThermo import H2ONaCl
sw_84 = H2ONaCl.cH2ONaCl("IAPS84")
sw_95 = H2ONaCl.cH2ONaCl("IAPWS95")

def plot_3d():
    fig=plt.figure(figsize=(14,14))
    ax = fig.add_subplot(111,projection='3d',facecolor='None')
    helpfunc.set_axis_diagram_3D(ax)
    # calculate critical curve
    sw=H2ONaCl.cH2ONaCl('IAPS84')
    T=np.linspace(sw.Tmin(), sw.Tmax(), 200)
    P,X=np.array(sw.P_X_Critical(T))
    # plot
    ax.plot(X*100, T-273.15, P/1E5, label='Critical curve', color='r')

    savefig('CriticalCurve_3D')

def benchmark_CriticalCurve(sw,mmc2='../Driesner2007b/1-s2.0-S0016703707002955-mmc2.txt'):
    T=np.linspace(sw.Tmin(), sw.Tmax(), 200)
    P,X=np.array(sw.P_X_Critical(T))
    T0,P0,X0=[],[],[]
    # try to open Driesner's result file
    data=np.loadtxt(mmc2,skiprows=6)
    T0,P0,X0,Rho0,H0=data[:,0],data[:,1],data[:,2],data[:,3],data[:,4]
    P_,X_wt_=np.array(sw.P_X_Critical(T0+273.15))
    X_=np.array(sw.Wt2Mol(X_wt_))
    Rho_=np.array(sw.Rho_phase(T0+273.15, P_, X_wt_, H2ONaCl.Liquid))
    H_=np.array(sw.H_phase(T0+273.15, P_, X_wt_, H2ONaCl.Liquid))
    Data0 = {'p':P0,'X':X0,'rho':Rho0,'h':H0}
    Data_={'p':P_/1E5,'X':X_,'rho':Rho_,'h':H_}
    Err,RErr={},{}
    for key in Data0.keys(): Err[key],RErr[key] = Data0[key]-Data_[key], np.abs(Data0[key]-Data_[key])/(Data0[key])*100.0
    # print to file and compare
    fpout = open('%s/mmc2_%s.csv'%(result_path,sw.name_backend()),'w')
    fpout.write('T[deg.C],P(Driesner)[bar],P(xThermo)[bar],P(diff)[bar],X(Driesner)[mol],X(xThermo)[mol],X(diff)[mol],Rho(Driesner)[kg/m3],Rho(xThermo),Rho(err),H(Driesner)[J/kg],H(xThermo),H(err)\n')
    for i in range(0,len(T0)):
        fpout.write('%.6e'%(T0[i]))
        for key in Data0.keys():
            fpout.write(',%.6e,%.6e,%.6e'%(Data0[key][i], Data_[key][i],compare(Data0[key][i],Data_[key][i])))
        fpout.write('\n')
    fpout.close()

    # plot
    fig,axes=plt.subplots(1,3, figsize=(12,3),gridspec_kw={'width_ratios':[1, 1, 1],'wspace':0.3})
    axes_err=['']*len(axes)
    for i,ax in enumerate(axes):
        axes_err[i]=ax.inset_axes([0,1,1,0.3])
        axes_err[i].set_yscale('log')
        # axes_err[i].set_ylim(1E-6,5E-3)
        axes_err[i].set_ylabel('RE(%)')
        axes_err[i].text(-0.08,1.0,'(%s)'%(chr(97+i)),ha='right',va='bottom',fontsize=10,fontweight='bold',transform=axes_err[i].transAxes)
    # 1. critical curve
    ax,ax_err=axes[0],axes_err[0]
    l,=ax.plot(T-273.15,P/1E5, color='r',label='xThermo',lw=4)
    if(len(T0)>0): ax.plot(T0,P0,ls='dashed',color='lightgray',label='Driesner(2007b)')
    ax.set_xlabel('Temperature ($^{\circ}$C)')
    ax.set_ylabel('Critical pressure (bar)',color=l.get_color())
    ax_err.bar(T0+2.5, RErr['p'],color=l.get_color(),width=5)
    # ax.yaxis.set_minor_locator(MultipleLocator(100))
    ax.legend(loc='upper left')
    # ax.text(0.005,0.98,'(a)',transform=ax.transAxes,ha='left',va='top',fontsize=12,fontweight='bold')
    ax_X = ax.twinx()
    l,=ax_X.plot(T-273.15,X*100,label='blue',lw=4)
    ax_X.set_ylim(0, ax_X.get_ylim()[1])
    if(len(T0)>0): ax_X.plot(T0,np.array(sw.Mol2Wt(X0))*100,ls='dashed',color='lightgray')
    ax_X.set_ylabel('Critical composition (wt.% NaCl)',color=l.get_color())
    ax_err.bar(T0-2.5, RErr['X'],color=l.get_color(),width=5)
    # 2. density
    ax,ax_err=axes[1],axes_err[1]
    ax.plot(T0, Rho_,lw=4,label='xThermo')
    ax.plot(T0, Rho0, ls='dashed',color='lightgray',label='Driesner(2007b)')
    ax_err.bar(T0, RErr['rho'],width=5)
    ax.yaxis.set_ticks_position('right')
    ax.yaxis.set_label_position('right')
    ax.set_ylabel('Density (km/m$^{\mathregular{3}}$)')
    ax.set_xlabel('Temperature ($^{\circ}$C)')
    ax.legend()
    # 3. specific enthalpy
    ax,ax_err=axes[2],axes_err[2]
    ax.plot(T0, H_/1E6,lw=4,label='xThermo')
    ax.plot(T0, H0/1E6, ls='dashed',color='lightgray',label='Driesner(2007b)')
    ax.yaxis.set_ticks_position('right')
    ax.yaxis.set_label_position('right')
    ax.set_ylabel('Specific enthalpy (MJ/kg)')
    ax.set_xlabel('Temperature ($^{\circ}$C)')
    ax_err.bar(T0, RErr['h'],width=5)
    ax.legend()
    # set axes
    for i,ax in enumerate(axes):
        axes_err[i].set_xlim(ax.get_xlim())
        axes_err[i].xaxis.set_ticks([])
        ax.xaxis.set_minor_locator(MultipleLocator(40))
        ax.grid(which='major',lw=0.02,color='k')
        ax.grid(which='minor',lw=0.01,color='gray')

    # statistics of the difference
    table=[]
    for key,name in zip(list(Err.keys()),['Pressure (bar)','Composition (mole fraction)','Density (kg/m3)','Specific enthalpy (J/kg)']):
        RErr[key] = RErr[key][~(np.isnan(RErr[key]) | np.isinf(RErr[key]))]
        table.append([name,Err[key].min(),Err[key].max(),RErr[key].min(),RErr[key].max()])
    print(tabulate(table, headers=['Critical property', 'Err. Min', 'Err. Max','RE. Min(%)','RE. Max(%)'],numalign="right",floatfmt=".6f"))
    savefig('H2ONaCl_CriticalCurve')
    return T0,P0

def plot_critpT_H2O(T_crit,P_crit,cmap='GnBu'):
    T,p = np.linspace(274,T_crit.max(),100), np.linspace(1E5,P_crit.max(),100)
    TT,PP = np.meshgrid(T,p)
    prop = np.zeros_like(TT)
    iaps84 = H2O.cIAPS84()
    iapws95 = H2O.cIAPWS95_CoolProp()
    for i in range(0,TT.shape[0]):
        for j in range(0,TT.shape[1]):
            props = iapws95.UpdateState_TPX(TT[i][j], PP[i][j])
            prop[i][j] = props.Rho
    fig,axes=plt.subplots(1,2,figsize=(12,4),gridspec_kw={'wspace':0.25})
    ax=axes[0]
    CS = ax.contourf(TT-273.15,PP/1E5, prop, levels=50, cmap=cmap)
    ax_cb = ax.inset_axes([1.01, 0, 0.05, 1])
    plt.colorbar(CS, cax=ax_cb, orientation='vertical',label='%s (%s)'%('Density','kg/$m^3$'))
    l,=ax.plot(T_crit-273.15, P_crit/1E5,color='r',lw=2,label='Critical p,T of $H_{\mathregular{2}}$O-NaCl system')
    x0,y0=T_crit[int(len(T_crit)/3*2)]-273.15, P_crit[int(len(P_crit)/3*2)]/1E5
    ax.annotate("Critical p,T of\nH$_{\mathregular{2}}$O-NaCl system",
                xy=(x0,y0),xytext=(x0-100,y0), ha='right',va='center',bbox={'fc':'None','ec':l.get_color()},fontsize=14,fontweight='bold',
                arrowprops=dict(arrowstyle="->",connectionstyle="arc3"),)
    # labels
    # ax.text(0.98,0.98,water.name(),ha='right',va='top',bbox={'fc':'w','ec':'gray'}, transform=ax.transAxes)
    ax.set_xlabel('Temperature ($^{\circ}$C)')
    ax.set_ylabel('Pressure (bar)')
    # IAPS84 - IAPWS95
    rho_84,rho_95,h_84,h_95=np.zeros_like(T_crit),np.zeros_like(T_crit),np.zeros_like(T_crit),np.zeros_like(T_crit)
    for i in range(0,len(T_crit)):
        props_84 = iaps84.UpdateState_TPX(T_crit[i],P_crit[i])
        props_95 = iapws95.UpdateState_TPX(T_crit[i],P_crit[i])
        rho_84[i],rho_95[i],h_84[i],h_95[i] = props_84.Rho, props_95.Rho, props_84.H, props_95.H
    ax=axes[1]
    barwidth=5
    ax.set_yscale('log')
    ax.bar(T_crit-273.15-barwidth/2,np.abs(rho_84-rho_95)/rho_84*100,width=barwidth,label='Density')
    ax.bar(T_crit-273.15+barwidth/2,np.abs(h_84-h_95)/h_84*100,width=barwidth,label='Specific enthalpy')
    ax.legend(ncol=2,title='Relative difference: $\\frac{|IAPS84-IAPWS95|}{IAPS84}\\times100$')
    ax.set_ylabel('Relative difference (%)')
    ax.set_xlabel('Temperature ($^{\circ}$C)')
    ax.yaxis.set_label_position('right')
    ax.yaxis.set_ticks_position('right')
    savefig('CriticalCurve_on_H2O')
# %%
# General 3D view
# --------------------------------
plot_3d()

# %%
# Based on IAPS84 EOS
# --------------------------------
T_crit,P_crit=benchmark_CriticalCurve(sw_84)

# %%
# Based on IAPWS95 EOS
# --------------------------------
T_crit,P_crit=benchmark_CriticalCurve(sw_95)

# %%
# H2O properties at critical p,T condition of H2O-NaCl
# ----------------------------------------------------------------
plot_critpT_H2O(T_crit+273.15,P_crit*1E5)

# %%
# Result table
# -----------------------------
# .. seealso::
#
#     |mmc2| in :cite:`Driesner2007Part2` and Fig. 1,5,6 in :cite:`Driesner2007Part1`.
#
# Result data calculated by |xThermo| based on both water EOS of IAPS84 and IAPWS95.
#
# .. tab:: IAPS84
#
#     .. csv-table:: Comparison between result of :cite:`Driesner2007Part2` and result calculated by |xThermo|.
#         :file: mmc2_IAPS84.csv
#         :header-rows: 1
#
# .. tab:: IAPWS95
#
#     .. csv-table:: Comparison between result of :cite:`Driesner2007Part2` and result calculated by |xThermo|.
#         :file: mmc2_IAPWS95.csv
#         :header-rows: 1
#
#
# .. tip::
#
#     The help function for 3D plot can be downloaded at here: :download:`helpfunc.py`