from math import *

framerate = 30
temporal_res = 1/framerate #TR
num_time_points = 5*60*framerate #ntp
num_events = 30
num_reps = 5
min_resp_delay = floor(1/temporal_res)*temporal_res  #psdmin
max_resp_delay = floor(5/temporal_res)*temporal_res  #psdmax
delta_resp_delay = temporal_res    #dPSD
min_null_delay = floor(1/temporal_res)*temporal_res  #tnullmin
stim_duration = floor(0.5/temporal_res)*temporal_res
num_search = 1000
num_kept_seq = 3
output_name = 'bah'

#generate the event string
ev_str = ''
for i in range(num_events):
    ev_str += '--ev Event_'+ str(i) + ' ' + str(stim_duration) + ' ' +str(num_reps) +' '

optstr = 'optseq2 --ntp ' + str(num_time_points) + ' --tr ' + str(temporal_res) + \
         ' --psdwin ' + str(min_resp_delay) + ' ' + str(max_resp_delay) + ' ' + \
        str(delta_resp_delay) + ' ' + ev_str + '--nkeep ' + str(num_kept_seq) +\
        ' --tnullmin ' + str(min_null_delay) + ' --nsearch ' + str(num_search) + ' --o ' + output_name
print(optstr)
