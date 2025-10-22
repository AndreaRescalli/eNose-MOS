/**
 *
 * \file  Utils.c
 * \brief Source file with utility functions.
 *
 * \author Damiano Rosario Tasso, Andrea Rescalli
 * \date   05/05/2023
 *
 */


#include "Utils.h"


/**
 * \brief Function that inits all the components.
 *
 * \param[in] void
 * \return void
*/
void Utils_StartComponents(void) {
    
    CyDelay(100);
    
    EEPROM_Start();
    
    UART_Start();
    I2C_Master_Start();
    
    Watchdog_Start();
    
    Internal_MUX_Start();
    ADC_DelSig_Start();
    AMUX_EN_Write(LOW); 
    AMUX_NEN_Write(LOW); 
    AMUX_A0_Write(LOW); 
    AMUX_A1_Write(LOW);
    AMUX_A2_Write(LOW);
    TimerADC_Start();
    
    PUMP_IN_Write(LOW); 
    PUMP_OUT_Write(LOW); 
    VALVE_IN_Write(LOW);
    VALVE_OUT_Write(LOW);
    
    PWM_S4_HC_12_Start();
    PWM_S4_HC_34_Start();
    PWM_S6_HC_Start();
    PWM_AS_HC_Start();
    Timer200ms_Start();
    
    CyDelay(1000);
 
} // end Utils_StartComponents



/*
*   \brief Prepare Global data buffer.
*
*   This function creates a data buffer containing the gas 
*   sensors voltage (in digit) and bme280's data. 
*
*   \param[in] gas_sens : Pointer to the gas_sensor struct 
*   \param[in] data_bme : Pointer to bme280 data struct
*/
void BundleData(Gas_Sensor* gas_sens, BME280* data_bme) {
    
    // Get pointer to struct to Gas sensor voltage and BME data. 
    Gas_Sens_Voltage *volt_data = &gas_sens->Gas_Volt_Data;
    BME280_Data *bme280 = &data_bme->data; 
    
    GlobalBuffer[1] += 1;
  
    // Data bundle
    GlobalBuffer[2]  = (volt_data->S4_1_v & MSB)  >> 24;
    GlobalBuffer[3]  = (volt_data->S4_1_v & CSB1) >> 16;
    GlobalBuffer[4]  = (volt_data->S4_1_v & CSB2) >> 8;
    GlobalBuffer[5]  = (volt_data->S4_1_v & LSB);
    GlobalBuffer[6]  = (volt_data->S4_2_v & MSB)  >> 24;
    GlobalBuffer[7]  = (volt_data->S4_2_v & CSB1) >> 16;
    GlobalBuffer[8]  = (volt_data->S4_2_v & CSB2) >> 8;
    GlobalBuffer[9]  = (volt_data->S4_2_v & LSB);
    GlobalBuffer[10]  = (volt_data->S4_3_v & MSB)   >> 24;
    GlobalBuffer[11] = (volt_data->S4_3_v & CSB1) >> 16;
    GlobalBuffer[12] = (volt_data->S4_3_v & CSB2) >> 8;
    GlobalBuffer[13] = (volt_data->S4_3_v & LSB);
    GlobalBuffer[14] = (volt_data->S4_4_v & MSB)  >> 24;
    GlobalBuffer[15] = (volt_data->S4_4_v & CSB1) >> 16;
    GlobalBuffer[16] = (volt_data->S4_4_v & CSB2) >> 8;
    GlobalBuffer[17] = (volt_data->S4_4_v & LSB);
    GlobalBuffer[18] = (volt_data->S6_1_v & MSB)  >> 24;
    GlobalBuffer[19] = (volt_data->S6_1_v & CSB1) >> 16;
    GlobalBuffer[20] = (volt_data->S6_1_v & CSB2) >> 8;
    GlobalBuffer[21] = (volt_data->S6_1_v & LSB);
    GlobalBuffer[22] = (volt_data->S6_2_v & MSB)  >> 24;
    GlobalBuffer[23] = (volt_data->S6_2_v & CSB1) >> 16;
    GlobalBuffer[24] = (volt_data->S6_2_v & CSB2) >> 8;
    GlobalBuffer[25] = (volt_data->S6_2_v & LSB);
    GlobalBuffer[26] = (volt_data->AS_1_v & MSB)  >> 24;
    GlobalBuffer[27] = (volt_data->AS_1_v & CSB1) >> 16;
    GlobalBuffer[28] = (volt_data->AS_1_v & CSB2) >> 8;
    GlobalBuffer[29] = (volt_data->AS_1_v & LSB);
    GlobalBuffer[30] = (volt_data->AS_2_v & MSB)  >> 24;
    GlobalBuffer[31] = (volt_data->AS_2_v & CSB1) >> 16;
    GlobalBuffer[32] = (volt_data->AS_2_v & CSB2) >> 8;
    GlobalBuffer[33] = (volt_data->AS_2_v & LSB);
   
    // BME280 bundle data
    // Press
    GlobalBuffer[34] = ((uint8_t) (bme280->pressure >> 24) & 0xFF);
    GlobalBuffer[35] = ((uint8_t) (bme280->pressure >> 16) & 0xFF);
    GlobalBuffer[36] = ((uint8_t) (bme280->pressure >> 8) & 0xFF);
    GlobalBuffer[37] = ((uint8_t) (bme280->pressure) & 0xFF);
    // Temperature
    GlobalBuffer[38] = ((uint8_t) (bme280->temperature >> 24) & 0xFF);
    GlobalBuffer[39] = ((uint8_t) (bme280->temperature >> 16) & 0xFF);
    GlobalBuffer[40] = ((uint8_t) (bme280->temperature >> 8) & 0xFF);
    GlobalBuffer[41] = ((uint8_t) (bme280->temperature) & 0xFF);
    // Humidity
    GlobalBuffer[42] = ((uint8_t) (bme280->humidity >> 24) & 0xFF);
    GlobalBuffer[43] = ((uint8_t) (bme280->humidity >> 16) & 0xFF);
    GlobalBuffer[44] = ((uint8_t) (bme280->humidity >> 8) & 0xFF);
    GlobalBuffer[45] = ((uint8_t) (bme280->humidity) & 0xFF);
    
} // end BundleData


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
int32 GasSensor_VoltRead(void) {
    
    int32 value_dig  = 0; 
    
    // Reading the digit value from ADCDelSig --> int32
    value_dig = ADC_DelSig_Read32(); 
    
    if(value_dig > 65535) {
        value_dig = 65535;
    }
    else if (value_dig <= 0) {
        value_dig = 0;
    }
    
    return value_dig;
    
} // end GasSensor_VoltRead

/* [] END OF FILE */
