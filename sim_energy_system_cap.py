# sim_energy_system_cap.py
#
# Usage:  python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s
#  script will implement a simulation for a capacitor based energy system
# Parameters:
# sa_m2: solar cell surface area 
# eff: solar cell efficiency
# voc: solar array open circuit voltage 
# c_f: energy buffer capacitance 
# r_esr: capacitor effective series resistance 
# q0_c: initial charge of capacitor 
# p_on_w:power draw during operation
# v_thresh: voltage threshold for power off 
# dt_s:simulation time step in seconds
# dur_s: simulation duration in seconds 
# Output:
#  A description of the script output
#
# Written by Anushka Devarajan
# Other contributors: None
#
# Optional license statement, e.g., See the LICENSE file for the license.

# import Python modules
import math # math module
import sys # argv
import csv 

# "constants"
irr_w_m2 = 1366.1 #W/m^2

# helper functions

## function description
#def calc_solar_current(irr_w_m2, sa_m2, eff, voc):
    

# initialize script arguments
sa_m2= float('nan')
eff= float('nan')
voc= float('nan')
c_f= float('nan')
r_esr= float('nan')
q0_c= float('nan')
p_on_w= float('nan')
v_thresh= float('nan')
dt_s= float('nan')
dur_s= float('nan')


# parse script arguments
if len(sys.argv)==11:
    sa_m2= float(sys.argv[1])
    eff= float(sys.argv[2])
    voc= float(sys.argv[3])
    c_f= float(sys.argv[4])
    r_esr= float(sys.argv[5])
    q0_c= float(sys.argv[6])
    p_on_w= float(sys.argv[7])
    v_thresh= float(sys.argv[8])
    dt_s= float(sys.argv[9])
    dur_s= float(sys.argv[10])
else:
   print(\
    'Usage: '\
    'python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s'\
   )
   exit()


# write script below this line
#utility functions 
def calc_solar_current(irr_w_m2, sa_m2, eff, voc):
    return (irr_w_m2*sa_m2*eff)/voc

def calc_node_discr(q_c, c_f, i_a, esr_ohm, power_w):
    return (q_c/c_f + i_a*esr_ohm)**2 - 4*power_w*esr_ohm

def calc_node_voltage(disc, q_c, c_f, i_a, esr_ohm):
    return (q_c/c_f + i_a*esr_ohm + math.sqrt(disc))/2

#set initial values
isc_a=calc_solar_current(irr_w_m2, sa_m2, eff, voc)
i1_a = isc_a
qt_c= q0_c
p_mode_w=p_on_w
t_s = 0.0

#calculate initial node discriminant 
node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
if(node_discr<0.0):
    p_mode_w = 0.0
    node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)

#calculate initial node voltage: 
node_v = calc_node_voltage(node_discr, qt_c, c_f, i1_a, r_esr)

# solar cell cannot produce current at high voltage
if voc<= node_v and i1_a!=0.0:
    i1_a=0.0

#energy consumers cannot operate at low voltage 
if node_v<v_thresh:
    p_mode_w=0.0

log=[]
while t_s<dur_s:
    #calculate the load current
    i3_a= p_mode_w/node_v
    #update charge:
    qt_c += (i1_a-i3_a)*dt_s
    if qt_c<0.0:
        qt_c=0.0

    #set solar array current: 
    i1_a = isc_a

    #power on after charging 
    if p_mode_w==0.0 and node_v>= voc:
     p_mode_w = p_on_w
    
    #calculate initial node discriminant
    node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
    if (node_discr<0.0):
        p_mode_w:0.0
        node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr,p_mode_w)
    
    node_v = calc_node_voltage(node_discr, qt_c, c_f, i1_a, r_esr)
    if voc<=node_v and i1_a!=0.0:
        i1_a = 0.0
    if node_v<v_thresh:
        p_mode_w =0.0
    log.append([t_s, node_v])
    # Increment time step
    t_s += dt_s

#pair to CSV 
with open('./log.csv',mode='w',newline='') as outfile:
  csvwriter = csv.writer(outfile)
  csvwriter.writerow(\
   ['t_s','volts']\
  )
  for e in log:
    csvwriter.writerow(e)