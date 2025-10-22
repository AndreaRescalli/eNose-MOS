/**
 *
 * \file  mux_functions.h
 * \brief Header file with external mux handling functions.
 *
 * \author Damiano Rosario Tasso
 * \date   01/04/2022
 *
 */


#include "mux_functions.h"

void MuxSelection(Gas_Sensor* gas_sens, uint8_t ch) {
    
    // Get pointer to struct to Gas sensor voltage. 
    Gas_Sens_Voltage *volt_data = &gas_sens->Gas_Volt_Data;
    
    // Check the input channel selection. 
    if((ch <= 7) && (ch >= 0)) {
        switch(ch) {
            case 0: 
                // Digital port init ad-hoc 
                AMUX_A0_Write(LOW);
                AMUX_A1_Write(LOW); 
                AMUX_A2_Write(LOW);
                
                // Reading S4_1
                AMUX_EN_Write(LOW); 
                volt_data->S4_1_v = GasSensor_VoltRead();
                S4_1_v = GasSensor_VoltRead();
                // Reading S4_3
                AMUX_EN_Write(HIGH);
                volt_data->S4_3_v = GasSensor_VoltRead();  
                S4_3_v = GasSensor_VoltRead();
                break;
            case 1: 
                // Digital port init ad-hoc 
                AMUX_A0_Write(HIGH);
                AMUX_A1_Write(LOW); 
                AMUX_A2_Write(LOW);
                
//                // Heater voltage reading
                
                break; 
            case 2: 
                // Digital port init ad-hoc 
                AMUX_A0_Write(LOW);
                AMUX_A1_Write(HIGH); 
                AMUX_A2_Write(LOW);
                
                // Reading AS_1
                AMUX_EN_Write(LOW);  
                volt_data->AS_1_v = GasSensor_VoltRead();   
                AS_1_v = GasSensor_VoltRead(); 
                
                // Reading S6_2
                AMUX_EN_Write(HIGH);
                volt_data->S6_2_v = GasSensor_VoltRead();
                S6_2_v = GasSensor_VoltRead();
                break;
            case 3: 
                // Digital port init ad-hoc 
                AMUX_A0_Write(HIGH);
                AMUX_A1_Write(HIGH); 
                AMUX_A2_Write(LOW);
                
//                // Heater voltage reading
                
                break;
            case 4: 
                // Digital port init ad-hoc 
                AMUX_A0_Write(LOW);
                AMUX_A1_Write(LOW); 
                AMUX_A2_Write(HIGH);
                                
                // Reading S6_1
                AMUX_EN_Write(LOW);
                volt_data->S6_1_v = GasSensor_VoltRead();
                S6_1_v = GasSensor_VoltRead();
                // Reading S4_4
                AMUX_EN_Write(HIGH); 
                volt_data->S4_4_v = GasSensor_VoltRead();
                S4_4_v = GasSensor_VoltRead();
                break;
            case 5: 
                // Digital port init ad-hoc 
                AMUX_A0_Write(HIGH);
                AMUX_A1_Write(LOW); 
                AMUX_A2_Write(HIGH);
                
//                // Heater voltage reading 
 
                break;
            case 6: 
                // Digital port init ad-hoc 
                AMUX_A0_Write(LOW);
                AMUX_A1_Write(HIGH); 
                AMUX_A2_Write(HIGH);
                
                // Reading S4_2
                AMUX_EN_Write(LOW); 
                volt_data->S4_2_v = GasSensor_VoltRead(); 
                S4_2_v = GasSensor_VoltRead(); 
                // Reading AS_2
                AMUX_EN_Write(HIGH); 
                volt_data->AS_2_v = GasSensor_VoltRead();  
                AS_2_v = GasSensor_VoltRead();
            
                break;
            case 7: 
                // Digital port init ad-hoc 
                AMUX_A0_Write(HIGH);
                AMUX_A1_Write(HIGH); 
                AMUX_A2_Write(HIGH);
                
//                // Heater voltage reading
                
                break;
            default: 
                break; 
        }
        
    }
} // end MuxSelection

/* [] END OF FILE */