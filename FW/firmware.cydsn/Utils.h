/**
 *
 * \file  Utils.h
 * \brief Header file with utility functions.
 *
 * \author Damiano Rosario Tasso, Andrea Rescalli
 * \date   05/05/2023
 *
 */

#ifndef __UTILS_H_
    #define __UTILS_H_
    
    // =============================================
    //                   INCLUDES
    // =============================================
    #include "cytypes.h"
    #include "MACROS.h"
    #include "project.h"
    #include "Gas_Sensor.h"
    #include "BME280.h"
    #include <stdio.h>
    
    
    
    // =============================================
    //               GLOBALS & FLAGS
    // =============================================
    
    
    
    
    // =============================================
    //                  FUNCTIONS
    // =============================================
    /**
     * \brief Function that starts all the components.
     *
     * \param[in] void
     * \return void
    */
    void Utils_StartComponents(void);
    
    
    /*
    *   \brief Reading Voltage from gas sensors.
    *
    *   This function uses the ADCDelSig API in order to sample
    *   the analog voltage signal on the gas sensor out pin. This
    *   digit output voltage value is cinverted in volt. 
    *
    *   \param[in] gas_sens : Pointer to the gas_sensor struct 
    * --------------------------------------------------------------------------------
    *   \return Gas sensor voltage output
    */
    int32 GasSensor_VoltRead(void);
    
    
    /*
    *   \brief Prepare Global data buffer.
    *
    *   This function creates a data buffer containing the gas 
    *   sensors voltage (in digit) and bme280's data. 
    *
    *   \param[in] gas_sens : Pointer to the gas_sensor struct 
    *   \param[in] data_bme : Pointer to bme280 data struct
    */
    void BundleData(Gas_Sensor* gas_sens, BME280* data_bme);    
    
#endif

/* [] END OF FILE */
