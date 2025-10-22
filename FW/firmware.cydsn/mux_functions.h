/**
 *
 * \file  mux_functions.h
 * \brief Header file with external mux handling functions.
 *
 * \author Damiano Rosario Tasso
 * \date   01/04/2022
 *
 */


#ifndef __MUX_FUNCTIONS_H__
    #define __MUX_FUNCTIONS_H__

    #include "MACROS.h"
    #include "Gas_Sensor.h"
    #include "Utils.h"
    
    /*
    *   \brief Internal MUX channel selection and signal reading. 
    *
    *   This function select the Mux channel according to the Hardware 
    *   design of the board. for each selection the sensor voltage signal
    *   was saved. 
    *
    *   \param[in] gas_sens : Pointer to the gas_sensor struct
    *   \param[in] ch       : Number of the selected Mux channel
    */
    void MuxSelection(Gas_Sensor* gas_sens, uint8_t ch); 
    
#endif
/* [] END OF FILE */