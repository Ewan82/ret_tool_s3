import numpy as np
import subprocess
import os
import sys
import itertools as itt
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import glob
#import netCDF4 as nc
import plot_ret as pr


def find_nearest(array, value):
    """
    Find nearest value in an array
    :param array: array of values
    :param value: value for which to find nearest element
    :return: nearest value in array, index of nearest value
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx


def run_ret_tool(out_dir, run_ret=True, **kwargs):
    """
    Wrapper to retrieval tool, can specify keyword args to retrival tool and will update accordingly
    :param out_dir: Directory to copy and run retrieval tool too (str)
    :param run_ret: if True runs retrieval tool (bool)
    :param kwargs: args to update in running retrieval tool
    :return: Updated dictionary of args passed to retrieval tool (dict)
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    ret_tool_dic = {'time_start': '20170323', 'time_end': '20170720', 'site_nml': dir_path+'/site_test_ss_508.nml', 'states_file':
                    False, 'obs_s1': False, 'obs_s2': False, 'no_use_prior': False, 'no_use_states': False, 'gtol':
                    1e0, 'dynmodunc_inifile': dir_path+'/mod_ini/dynmod_default.ini', 's1_unc': 0.001, 's2_relunc': 0.05,
                    's2_uncfloor': 0.001, 's1_vv_uncfloor': 0.004,
                    #'s1_pol': ['VH', 'HH'],
                    #'s2_bnds': ['2', '3', '4', '5', '6', '7', '8', '8a', '11', '12'],
                    'ctlvec_relunc': [1.0, 0.5, 0.5, 0.5], 'ctlvec_uncfloor': [1e-6, 1e-3, 1e-3, 1e-3],
                    's1_vh_uncfloor':0.00001}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value is not False:
                ret_tool_dic[key] = value
    if run_ret is True:
        subprocess.call(['cp', '-R', dir_path+'/ret_code_lai2', out_dir])
        #subprocess.call(['cp', '-R', dir_path + '/ret_code', out_dir])
        os.chdir(out_dir)
        subprocess.call(['make', 'setup'])
        cmd = ['bin/rs_pre.py', 'pre_general']
        for key in ret_tool_dic.keys():
            if ret_tool_dic[key] is not False:
                if type(ret_tool_dic[key]) is str:
                    print('str, '+key)
                    cmd.append('--'+key)
                    cmd.append(ret_tool_dic[key])
                elif type(ret_tool_dic[key]) is float:
                    print('float, '+key)
                    cmd.append('--'+key)
                    cmd.append(str(ret_tool_dic[key]))
                elif type(ret_tool_dic[key]) is list:
                    cmd.append('--'+key)
                    for x in ret_tool_dic[key]:
                        print(x)
                        cmd.append(str(x))
                else:
                    cmd.append('--'+key)
        subprocess.call(cmd)
        subprocess.call(['make', 'retrieval' , 'RETRARGXTRA=--no_fapar'])
        #subprocess.call(['make', 'mba'])
        os.chdir(dir_path)

    return ret_tool_dic


def save_plot_err(_dir, sname='mni_508_med_test.png', point='508_med', field_obs=True, exp_no=None):
    """
    Plots output from retrieval tool run with field obs
    :param _dir: directory to save plots and stats file in (str)
    :param sname: name to save figure (str)
    :param point: point location of plot and stats file (str)
    :param field_obs: plot field observations on top (bool)
    :param exp_no: number of experiment at point (int)
    :return: na
    """
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(14, 6),)
    pr.plot_var('sm', _dir, axes=ax[0], point=point, field_obs_on=field_obs)
    #fig.savefig(_dir + '/sm.png', bbox_inches='tight')
    pr.plot_var('lai', _dir, axes=ax[1], point=point, field_obs_on=field_obs)
    #fig.savefig(_dir + '/lai.png', bbox_inches='tight')
    pr.plot_var('canht', _dir, axes=ax[2], point=point, field_obs_on=field_obs)
    fig.autofmt_xdate()
    fig.savefig(_dir + '/'+sname, bbox_inches='tight')

    #fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 6),)
    #pr.plot_refl(_dir, point, axes=ax[0])
    #pr.plot_backscat(_dir, point, axes=ax[1])
    #fig.autofmt_xdate()
    #fig.savefig(_dir + '/r_b_'+sname, bbox_inches='tight')

    #fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(14, 8),)
    #pr.plot_refl_mod(_dir, point, axes=ax[0])
    #pr.plot_backscat_mod(_dir, point, axes=ax[1])
    #fig.autofmt_xdate()
    #fig.savefig(_dir + '/r_b_mod_'+sname, bbox_inches='tight')

    sm_stats = pr.save_stats('sm', _dir, point=point)
    lai_stats = pr.save_stats('lai', _dir, point=point)
    canht_stats = pr.save_stats('canht', _dir, point=point)
    stats_file = _dir + '/stats.txt'
    lines = []
    lines.append('experiment stats \n')
    lines.append('state_var: post rmse, post ubrmse, post corrcoef \n')
    lines.append('lai: %.2f, %.2f, %.2f \n' %(lai_stats[1], lai_stats[3], lai_stats[5]))
    lines.append('sm: %.2f, %.2f, %.2f \n' %(sm_stats[1], sm_stats[3], sm_stats[5]))
    lines.append('canht: %.2f, %.2f, %.2f \n' %(canht_stats[1], canht_stats[3], canht_stats[5]))
    f = open(stats_file, 'w')
    for line in lines:
        f.write(line)
    f.close()
    save_stat = '/home/users/ewanp82/projects/ret_tool_s3/'+point+'exp_stat.txt'
    with open(save_stat, 'a') as f:
        f.write(point+', %.3i, sm_cor: %.2f, lai_cor: %.2f \n' %(exp_no, sm_stats[5], lai_stats[5]))
        f.close()
    return 'stats saved! :-)'


def make_exps_508med_arr_test(point='508_med', date_start='20170323', date_end='20170720'):
    """
    Creates an array of multiple experiments for which to run the retrieval tool.
    :param point: point for which to run the retrieval tool (str)
    :param date_start: start date for retrieval tool (str)
    :param date_end:end date for retrieval tool (str)
    :return: set of experiments for which to run the retrival tool (list)
    """
    time_start = [date_start]  # ['20170324']
    time_end = [date_end]  # ['20170717']
    states_file = [#'/home/users/if910917/projects/ret_tool_s3/state_files/mni_retr_jules_prior.csv',
                   False
                   ]
    obs_s1 = ['/home/users/ewanp82/projects/ret_tool_s3/S1/mni_s1_'+point+'_hv.csv',
              #'/home/users/ewanp82/projects/ret_tool_s3/S1_new/mni_s1_' + point + '_vv.csv',
              #'/home/users/ewanp82/projects/ret_tool_s3/S1_new/mni_s1_'+point+'_hvvv.csv',
              #'/home/users/if910917/projects/ret_tool_s3/S1_new/mni_s1_' + point + '_2017.csv',
              False
              ]
    obs_s2 = [#'/home/users/ewanp82/projects/ret_tool_s3/S2_new/mni_s2_'+point+'_b4b8.csv',
              '/home/users/ewanp82/projects/ret_tool_s3/S2/mni_s2_'+point+'_b4b5b6b7b8b8a.csv',
              #'/home/users/ewanp82/projects/ret_tool_s3/S2_new/mni_s2_' + point + '_allbands.csv',
              #'/home/users/if910917/projects/ret_tool_s3/S2_new/mni_s2_' + point + '_2017.csv',
              False
              ]
    #no_use_prior = [False, True]
    #no_use_states = [False, True]
    dynmodunc_inifile = [#'/home/users/ewanp82/projects/ret_tool_s3/mod_ini/dynmod_default.ini',
                         #'/home/users/ewanp82/projects/ret_tool_s3/mod_ini/dynmod_tight.ini',
                         #'/home/users/ewanp82/projects/ret_tool_s3/mod_ini/dynmod_test.ini',
                         '/home/users/ewanp82/projects/ret_tool_s3/mod_ini/dynmod_vtight.ini',
                         #'/home/users/ewanp82/projects/ret_tool_s3/mod_ini/dynmod_test2.ini',
                         ]
    s1_unc = [1.6]#[0.1, 0.4, 0.8, 1.6]#[0.4]#[0.8]#
    s2_uncfloor = [0.02]#[0.001, 0.008, 0.02]#[0.008]#[0.001]#
    s2_relunc = [0.05]  #, 0.03]#[0.1] #
    ctlvec_relunc = [[0.01, 0.5, 0.05, 0.5],]  # [0.01, 0.5, 0.05, 0.5]]
    ctlvec_uncfloor = [[0.001, 3.0, 0.1, 0.05],]  # [0.001, 3.0, 1.0, 0.05]]
    #ctlvec_relunc = [[0.01, 0.5, 0.05, 0.5], [0.01, 0.5, 0.05, 0.5]]
    #ctlvec_uncfloor = [[0.001, 3.0, 0.1, 0.05], [0.001, 3.0, 1.0, 0.05]]
    #site_nml=['site_test_ss_508.nml', 'site_test_ss_508_2.nml', 'site_new_test.nml', 'site_new2.nml']
    #site_nml=['site_new2.nml']  # , 'site_new3.nml']
    site_nml = ['site_new_test.nml']  # , 'site_new3.nml']
    exp_list = [time_start, time_end, states_file, obs_s1, obs_s2, dynmodunc_inifile,
                s1_unc, s2_uncfloor, ctlvec_relunc, ctlvec_uncfloor, s2_relunc, site_nml]
    it_exp_list = list(itt.product(*exp_list))
    exp_list_final = [a for a in it_exp_list if a[3:5] != (False, False)]
    print('exp_list length: ', str(len(exp_list_final)))
    return exp_list_final


def run_retr_exp(exp_no, exp_tup, point='508_med', run_ret=True, field_obs=True):
    """
    For experiment in list past from make_exps_508med_arr_test function will run retrieval tool and plot results.
    :param exp_no: experiment number in list for which to run retrieval tool (int)
    :param exp_tup: list of experiments generated by make_exps_508med_arr_test function
    :param point: point for which to run retrieval tool (str)
    :param run_ret: if True run retrieval tool (bool)
    :param field_obs: if True plot field observations on figure (bool)
    :return: na
    """
    if type(exp_tup[2]) is str:
        prior = 'jules'
    else:
        prior = 'flat'
    try:
        s1_str = exp_tup[3].split('_')[-1][:-4]
    except(AttributeError):
        s1_str = 'nos1'
    try:
        s2_str = exp_tup[4].split('_')[-1][:-4]
    except(AttributeError):
        s2_str = 'nos2'
    #save_dir = '/home/users/ewanp82/projects/ret_tool_s3/plots/'+point+'/'+prior+'_'+s1_str+'_'+s2_str+'_'+str(exp_no)
    save_dir = '/gws/nopw/j04/odanceo/epinnington/sen_syn/'+point+'_'+prior+'_'+s1_str+'_'+s2_str+'_'+str(exp_no)
    #save_dir = '/home/users/ewanp82/projects/ret_tool_s3/jas_test'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ret_dic = run_ret_tool(save_dir, run_ret=run_ret, time_start=exp_tup[0], time_end=exp_tup[1], states_file=exp_tup[2],
                           obs_s1=exp_tup[3], obs_s2=exp_tup[4], dynmodunc_inifile=exp_tup[5], s1_unc=exp_tup[6],
                           s2_uncfloor=exp_tup[7], ctlvec_relunc=exp_tup[8], ctlvec_uncfloor=exp_tup[9],
                           s2_relunc=exp_tup[10], site_nml=dir_path+'/'+exp_tup[11])
                           #site_nml=dir_path+'/site_test_ss_'+point[:3]+'.nml')
    save_plot_err(save_dir, sname='mni_'+point+'_'+prior+'_'+s1_str+'_'+s2_str+'.png', point=point, field_obs=field_obs, exp_no=exp_no)
    stats_file = save_dir + '/exp_' + str(exp_no) + '_setup.txt'
    lines = []
    for key in ret_dic.keys():
        lines.append(key+': '+str(ret_dic[key])+'\n')
    f = open(stats_file, 'w')
    for line in lines:
        f.write(line)
    f.close()
    return 'experiment '+str(exp_no)+' done! :-)'


def exp_run_setup(point='508_med', run_ret=True, field_ob=True, date_start='20170323', date_end='20170720'):
    """
    Writes bash script which will run retrieval tool for desired point.
    :param point: point for which to write bash file (str)
    :return: na
    """
    exp_list = make_exps_508med_arr_test()
    run_dir = '/home/users/ewanp82/projects/ret_tool_s3/exps_run/'
    for x in range(len(exp_list)):
        run_file = run_dir+'exp_'+str(x)+'_'+ point +'.bash'
        lines = []
        lines.append('#!/bin/bash ' + '\n')
        lines.append('#SBATCH --partition=short-serial ' + '\n')
        lines.append('#SBATCH -o '+'exp_'+str(x)+'_'+ point +'.out ' + '\n')
        lines.append('#SBATCH -e '+'exp_'+str(x)+'_'+ point +'.err ' + '\n')
        lines.append('#SBATCH --time=02:00:00 ' + '\n')
        lines.append('cd ' + os.getcwd() + '\n')
        #lines.append('cd ' + run_dir + ' \n')
        lines.append('module unload jaspy \n')
        lines.append('module load jaspy/2.7 \n')
        lines.append('echo which python \n')
        lines.append('python run_retr_new.py ' + str(x) + ' ' + point + ' ' + str(run_ret) + ' ' + str(field_ob) +
                     ' ' + date_start + ' ' + date_end + '\n')
        f = open(run_file, 'w')
        for line in lines:
            f.write(line)
        f.close()
    return 'exp list written!'


def write_paper_exps():
    """
    Writes the experiments which are used within the sentinel synergy paper.
    :return: na
    """
    exp_run_setup('508_med', date_start='20170323', date_end='20170720')
    exp_run_setup('508_high', date_start='20170323', date_end='20170720')
    exp_run_setup('508_low', date_start='20170323', date_end='20170720')
    exp_run_setup('542_med', date_start='20170323', date_end='20170720')
    exp_run_setup('542_high', date_start='20170323', date_end='20170720')
    exp_run_setup('542_low', date_start='20170323', date_end='20170720')
    exp_run_setup('515_med', date_start='20170608', date_end='20170922')
    exp_run_setup('515_high', date_start='20170608', date_end='20170922')
    exp_run_setup('515_low', date_start='20170608', date_end='20170922')
    return 'experiment bash scripts written!'


if __name__ == "__main__":
    # main function will run experiment for given point (e.g. 508_med), and time period (e.g. '20170323' to '20170720').
    exp_list = make_exps_508med_arr_test(sys.argv[2], sys.argv[5], sys.argv[6])
    exp_no = int(sys.argv[1])
    point = sys.argv[2]
    run_ret = sys.argv[3] == 'True'
    field_ob = sys.argv[4] == 'True'
    run_retr_exp(exp_no, exp_list[exp_no], point, run_ret=run_ret, field_obs=field_ob)
    print('ran experiment '+str(exp_no))
