import sys, time

sys.path.insert(0,"../modules/xsmu")
sys.path.insert(0,"../modules/xtcon")
sys.path.insert(0,"../apps")
sys.path.insert(0,"../apps/widgets")
sys.path.insert(0,"../lib")

import xsmu
import tcon
import numpy as np
from XSMU_Constants import *

f = open("V-Data.txt", "w")
f.close()

# Set current source to some value
# Call function to measure voltage
# Loop over the measuring function
# Print out the voltage values

def set_DC_current (xsmu_driver, value, source_range):
    # Need a range input corresponding to value

    mode       = SOURCE_MODE_CS
    autorange  = AUTORANGE_ON
    range      = source_range

    xsmu_driver.setSourceParameters (mode, autorange, range, value)

def measure_voltage (xsmu_driver, xtcon_driver, iterations):
    
    f = open("V-Data.txt", "a")
    for index in range(iterations):
        voltage     = xsmu_driver.VM_getReading( filterLength = 1 )
        temperature = xtcon_driver.getSampleTemperature()
        f.write(str(voltage) + "," + str(temperature) + '\n')
    f.close() 	

def stabilize_temp (xtcon_driver, tolerance, monitoring_period):
    
    history = []
    
    print ("Stabilizing .. \n")
    
    while True :
        history.append(xtcon_driver.getSampleTemperature())
        
        if (len(history) < monitoring_period):
            continue
        else :
            fluctuation = max(history[-monitoring_period:-1]) - min(history[-monitoring_period:-1])
            print "Max : " + str (max(history[-monitoring_period:-1])) + "\tMin : " + str(min(history[-monitoring_period:-1]))
            
            if (np.abs(fluctuation) < tolerance):
                print ("Fluctuation : " + str(fluctuation))
                print ("Stable ..\n")
                break

def main():
	
	xtcon_driver  = tcon.Driver      ()
        xtcon_devices = xtcon_driver.scan()
	xtcon_driver.open(xtcon_devices[0])
	
	temperatures = []
	
	setpoint = float(raw_input ("Enter isothermal setpoint              (K) : "))
	temperatures.append (setpoint)
	response = raw_input ("Do you want to add another temperature setpoint? : y/n") 
	while (response == 'y'):
            setpoint = float(raw_input ("Enter isothermal setpoint              (K) : "))
            temperatures.append (setpoint)
            response = raw_input ("Do you want to add another temperature setpoint? : y/n")
	
	tolerance         = float(raw_input ("Tempereature Tolerance      (over 10 successive readings) (K) : "))
	monitoring_period = int  (raw_input ("Enter the monitoring period (Number of temperature readings)  : "))
	iterations        = int(raw_input("Enter Number of datapoints at each temperature : "))
            
        xsmu_driver  = xsmu.Driver()
        xsmu_driver.open("XSMU012A")
	
	for setpoint in temperatures:
            print ("Starting Isothermal Run at " + str(setpoint) + " K \n")
            xtcon_driver.setIsothermalSetpoint (setpoint)
            xtcon_driver.startIsothermalControl()
	
            # Stabilizes the temperature and waits for user to take an IV run from Qrius GUI
            stabilize_temp (xtcon_driver, tolerance, monitoring_period)

	
            Amplitudes   = [0.0]
            ranges       = [CM_RANGE_100uA]
	
            for i in range(len(Amplitudes)):

                DC_amplitude   = Amplitudes[i]    # A
                DC_range       = ranges[i]
	
                print ("Setting DC Current.. \n")
	
                set_DC_current  (xsmu_driver, DC_amplitude, DC_range)
                measure_voltage (xsmu_driver, xtcon_driver, iterations)
	
            xtcon_driver.stopIsothermalControl()
	
	set_DC_current (xsmu_driver, 0.0, ranges[0])
	xtcon_driver.close()
        xsmu_driver.close()

main()
