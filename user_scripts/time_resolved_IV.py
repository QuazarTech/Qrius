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

f = open("I-Data.txt", "w")
f.close()

# Set voltage source to some value
# Call function to measure current
# Loop over the measuring function
# Print out the current values

def set_DC_voltage (xsmu_driver, value):
    # No range input required
    # Only available range is VS_RANGE_10V
    
    mode       = SOURCE_MODE_VS
    autorange  = AUTORANGE_ON
    range      = VS_RANGE_10V

    xsmu_driver.setSourceParameters (mode, autorange, range, value)

def measure_current(xsmu_driver, xtcon_driver, iterations):
    
    f = open("I-Data.txt", "a")
    for index in range(iterations):
        current     = xsmu_driver .CM_getReading( filterLength = 1 )
        temperature = xtcon_driver.getSampleTemperature()
        f.write(str(current) + "," + str(temperature) + '\n')
    f.close() 	
   
def stabilize_temp (xtcon_driver, tolerance):
    
    history = []
    
    print ("Stabilizing .. \n")
    
    while True :
        history.append(xtcon_driver.getSampleTemperature())
        
        if (len(history)<200):
            continue
        else :
            fluctuation = max(history[-200:-1]) - min(history[-200:-1])
            print "Max : " + str (max(history[-200:-1])) + "\tMin : " + str(min(history[-200:-1]))
            
            if (np.abs(fluctuation) < tolerance):
                print ("Fluctuation : " + str(fluctuation))
                print ("Stable ..\n")
                break

def main():
	
	xtcon_driver  = tcon.Driver()
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
            
        tolerance      = float(raw_input ("Tempereature Tolerance (over 10 successive readings) (K) : "))
	monitoring_period = int  (raw_input ("Enter the monitoring period (Number of temperature readings)  : "))
	iterations        = int(raw_input("Enter Number of datapoints at each temperature : "))
	
	xsmu_driver  = xsmu.Driver()
	xsmu_driver.open("XSMU012A")
	
	for setpoint in temperatures:
            print ("Starting Isothermal Run at " + str(setpoint) + " K \n")
            xtcon_driver.setIsothermalSetpoint (setpoint)
            xtcon_driver.startIsothermalControl()
	
            # Stabilizes the temperature and waits for user to take an IV run from Qrius GUI
            stabilize_temp (xtcon_driver, tolerance)

	
            Amplitudes     = [0.0]
            
            for i in range(len(Amplitudes)):
                
                DC_amplitude   = Amplitudes[i]    # V
                
                print ("Setting DC Voltage.. \n")
	
                set_DC_voltage (xsmu_driver, DC_amplitude)
                measure_current(xsmu_driver, xtcon_driver, iterations)
	
            xtcon_driver.stopIsothermalControl()
	
	set_DC_voltage (xsmu_driver, 0.0)
	xtcon_driver.close()
        xsmu_driver.close()

main()
