/**
 *
 * \file  main.c
 * \brief Source file in charge of handling eNose project: temperature
 *        modulation patterns of 8 different MOS sensors.
 *
 * \author Andrea Rescalli
 * \date   05/05/2023
 *
 */
#include "project.h"
#include "Interrupts.h"
#include "ModulationPatterns.h"
#include "BME280.h"
#include "MACROS.h"
#include "Utils.h"

int main(void) {
    
    CyGlobalIntEnable; /* Enable global interrupts. */

    // Init components
    Utils_StartComponents();
    
    
    // Init flags and variables
    pwm_cmp_value           = 0;
    state                   = IDLE;
    
    BME280_ErrorCode        error;
    
    char rx                 = 0;
    flag_rx                 = 0;
    flag_stream             = 0;
    flag_enable_ramp        = 0;
    flag_enable_square      = 0;
    flag_enable_sine        = 0;
    flag_enable_triangle    = 0;
    flag_enable_sqtr        = 0;
    
    flag_200ms              = 0;
    flag_ramp_increment     = 0;
    flag_sine_increment     = 0;
    sine_dc                 = 0;
    lut_idx                 = 0;
    sine_cmp                = 0;
    flag_trng_increment     = 0;
    trng_state              = UP;
    flag_sqtr_increment     = 0;
    sqtr_dc                 = 0;
    lut_sqtr_idx            = 0;
    sqtr_cmp                = 0;
    counter                 = -1;
    
    flag_five_sec           = 0;
    counter_wtd             = 0;
    flag_settings           = 0;
    flag_new_setting_ready  = 0;
    flag_hum_setting        = 0;
    flag_temp_setting       = 0;
    flag_press_setting      = 0;
    flag_sb_time_setting    = 0;
    flag_filt_coeff         = 0;
    
    flag_read_gas           = 0;
    flag_read_bme           = 0;
    flag_read_data          = 0;
    
    
    // Data bundling
    BME280_ActualSettings[0]                             = BME280_ACTUAL_SETTINGS_HEADER;
    BME280_ActualSettings[1]                             = EEPROM_ReadByte(EEPROM_H_OSR);
    BME280_ActualSettings[2]                             = EEPROM_ReadByte(EEPROM_T_OSR);
    BME280_ActualSettings[3]                             = EEPROM_ReadByte(EEPROM_P_OSR);
    BME280_ActualSettings[4]                             = EEPROM_ReadByte(EEPROM_SB_TIME);
    BME280_ActualSettings[5]                             = EEPROM_ReadByte(EEPROM_FILT);
    BME280_ActualSettings[BME280_DEF_SETTING_PACKET - 1] = BME280_ACTUAL_SETTINGS_TAIL;
    
    uint8_t temp_settings[BME280_DEF_SETTING_PACKET]     = {0};
    
    
    GlobalBuffer[0]                                       = DATA_HEADER;
    GlobalBuffer[1]                                       = 0; // packet counter
    GlobalBuffer[DATA_BUFFER_SIZE - 1]                    = DATA_TAIL; 
    
    
    // Start BME280 operation
    error = BME280_Start(&bme280);
    if (error == BME280_OK) {        
        // BME280 Registers initialization 
        BME280_SetRegisters(&bme280, BME280_ActualSettings);
    }
    else {
        UART_PutString("Could not initialize sensor\r\n");
    }
    
    
    // Init ISRs
    ISR_RX_StartEx(Custom_ISR_RX);
    ISR_TIMER200ms_StartEx(Custom_ISR_TIMER200ms);
    ISR_WATCHDOG_StartEx(Custom_ISR_WATCHDOG);
    ISR_ADC_StartEx(Custom_ISR_ADC);
    

    for(;;) {
        
        if(flag_rx) {
            
            // Reset the watchdog timer
            Reset_WatchdogTimer();
        
            flag_rx = 0;
            state++;
            rx = UART_ReadRxData();
            
            // Handle possible user requested commands
            switch(rx) {
                case 'v': 
                    // Connection string sent
                    UART_PutString("COM Connection $$$");            
                    break;
                case 'r':
                    if(!flag_enable_ramp     &&
                       !flag_enable_square   &&
                       !flag_enable_sine     &&
                       !flag_enable_triangle &&
                       !flag_enable_sqtr) {
                        flag_enable_ramp     = 1;
                        flag_enable_square   = 0;
                        flag_enable_sine     = 0;
                        flag_enable_triangle = 0;
                        flag_enable_sqtr     = 0;
                    
                        // Reset Timers
                        Reset_TIMER();
                    }
                    break;
                case 'q':
                    if(!flag_enable_ramp     &&
                       !flag_enable_square   &&
                       !flag_enable_sine     &&
                       !flag_enable_triangle &&
                       !flag_enable_sqtr) {
                        flag_enable_ramp     = 0;
                        flag_enable_square   = 1;
                        flag_enable_sine     = 0;
                        flag_enable_triangle = 0;
                        flag_enable_sqtr     = 0;
                    
                        // Reset Timers
                        Reset_TIMER();
                    }
                    break;
                case 'w':
                    if(!flag_enable_ramp     &&
                       !flag_enable_square   &&
                       !flag_enable_sine     &&
                       !flag_enable_triangle &&
                       !flag_enable_sqtr) {
                        flag_enable_ramp     = 0;
                        flag_enable_square   = 0;
                        flag_enable_sine     = 1;
                        flag_enable_triangle = 0;
                        flag_enable_sqtr     = 0;
                    
                        // Reset Timers
                        Reset_TIMER();
                    }
                    break;
                case 't':
                    if(!flag_enable_ramp     &&
                       !flag_enable_square   &&
                       !flag_enable_sine     &&
                       !flag_enable_triangle &&
                       !flag_enable_sqtr) {
                        flag_enable_ramp     = 0;
                        flag_enable_square   = 0;
                        flag_enable_sine     = 0;
                        flag_enable_triangle = 1;
                        flag_enable_sqtr     = 0;
                    
                        // Reset Timers
                        Reset_TIMER();
                    }
                    break;
                case 'c':
                    if(!flag_enable_ramp     &&
                       !flag_enable_square   &&
                       !flag_enable_sine     &&
                       !flag_enable_triangle &&
                       !flag_enable_sqtr) {
                        flag_enable_ramp     = 0;
                        flag_enable_square   = 0;
                        flag_enable_sine     = 0;
                        flag_enable_triangle = 0;
                        flag_enable_sqtr     = 1;
                    
                        // Reset Timers
                        Reset_TIMER();
                    }
                    break;
                case 'a':
                    if(!flag_stream) {
                        flag_stream         = 1;
                    
                        // Disable patterns, we start only when user wants
                        // (in this way we can stream data from the beginning, but start
                        // the modulation later)
                        flag_enable_ramp     = 0;
                        flag_enable_square   = 0;
                        flag_enable_sine     = 0;
                        flag_enable_triangle = 0;
                        flag_enable_sqtr     = 0;
                    
                        // Reset Timers
                        Reset_TIMER();
                    }
                    break;
                case 's':
                    flag_stream      = 0;   
                    
                    // Disable patterns
                    flag_enable_ramp     = 0;
                    flag_ramp_increment  = 0;
                    flag_enable_square   = 0;
                    flag_enable_sine     = 0;
                    flag_sine_increment  = 0;
                    flag_enable_triangle = 0;
                    flag_trng_increment  = 0;
                    flag_enable_sqtr     = 0;
                    
                    // Stop heaters pattern
                    // Enable output
                    Control_Reg_KILL_PWM_Write(ENABLE_PWM);
                    // S4
                    PWM_S4_HC_12_WriteCompare1(0);
                    PWM_S4_HC_12_WriteCompare2(0);
                    PWM_S4_HC_34_WriteCompare1(0);
                    PWM_S4_HC_34_WriteCompare2(0);
                    // S6
                    PWM_S6_HC_WriteCompare1(0);
                    PWM_S6_HC_WriteCompare2(0);
                    // AS
                    PWM_AS_HC_WriteCompare1(0);
                    PWM_AS_HC_WriteCompare2(0);
                    
                    // Reset Timers
                    Reset_TIMER();
                    break;
                case 'O':
                    // !Heater full on!
                    
                    // Disable patterns
                    flag_enable_ramp     = 0;
                    flag_ramp_increment  = 0;
                    flag_enable_square   = 0;
                    flag_enable_sine     = 0;
                    flag_sine_increment  = 0;
                    flag_enable_triangle = 0;
                    flag_trng_increment  = 0;
                    flag_enable_sqtr     = 0;
                    
                    // Stop heaters pattern
                    // Enable output
                    Control_Reg_KILL_PWM_Write(ENABLE_PWM);
                    // S4
                    PWM_S4_HC_12_WriteCompare1(0);
                    PWM_S4_HC_12_WriteCompare2(0);
                    PWM_S4_HC_34_WriteCompare1(0);
                    PWM_S4_HC_34_WriteCompare2(0);
                    // S6
                    PWM_S6_HC_WriteCompare1(0);
                    PWM_S6_HC_WriteCompare2(0);
                    // AS
                    PWM_AS_HC_WriteCompare1(0);
                    PWM_AS_HC_WriteCompare2(0);
                    
                    // Reset Timers
                    Reset_TIMER();
                    break;
                case 'o':
                    // !Heater off!
                    
                    // Disable patterns
                    flag_enable_ramp     = 0;
                    flag_ramp_increment  = 0;
                    flag_enable_square   = 0;
                    flag_enable_sine     = 0;
                    flag_sine_increment  = 0;
                    flag_enable_triangle = 0;
                    flag_trng_increment  = 0;
                    flag_enable_sqtr     = 0;
                    
                    // Stop heaters pattern
                    // Disable output
                    Control_Reg_KILL_PWM_Write(DISABLE_PWM);
                    
                    // Reset Timers
                    Reset_TIMER();
                    break;
                case 'g': 
                    // Send BME280 default settings to GUI
                    flag_settings = 1;
                    break;                
                case 'h':
                    // Pump and Valve (IN) activation
                    PUMP_IN_Write(HIGH);                    
                    CyDelay(5);
                    VALVE_IN_Write(HIGH);   
                    
                    // Pump and Valve (OUT) disable
                    PUMP_OUT_Write(LOW);
                    VALVE_OUT_Write(LOW);
                    break;                    
                //case 'z': 
                    // Pump and Valve (IN) disable
                    //PUMP_IN_Write(LOW);
                    //VALVE_IN_Write(LOW);                    
                    //break;
                case 'y':
                    // Pump and Valve (OUT) activation
                    PUMP_OUT_Write(HIGH);                    
                    CyDelay(5);
                    VALVE_OUT_Write(HIGH);  
                    
                    // Pump and Valve (IN) disable
                    PUMP_IN_Write(LOW);
                    VALVE_IN_Write(LOW);
                    break;               
                //case 'j': 
                    // Pump and Valve (OUT) disable
                    //PUMP_OUT_Write(LOW);
                    //VALVE_OUT_Write(LOW);                    
                    //break;                     
                case 'e':
                    // Pump and Valve (IN) activation
                    PUMP_IN_Write(HIGH);
                    CyDelay(5);
                    VALVE_IN_Write(HIGH);
                    
                    // Pump and Valve (OUT) activation
                    PUMP_OUT_Write(HIGH);                    
                    CyDelay(5);
                    VALVE_OUT_Write(HIGH);                    
                    break;
                case 'i':
                    // Pump and Valve (IN) disable
                    PUMP_IN_Write(LOW);
                    VALVE_IN_Write(LOW);
                    
                    // Pump and Valve (OUT) disable
                    PUMP_OUT_Write(LOW);
                    VALVE_OUT_Write(LOW);                    
                    break;
                default:
                    break;
            } // end switch-case rx
            
            
            // Switch-case used to read the incoming information about the BME280 settings change
            switch(state) {                
                case HEAD: 
                    if(rx == BME280_SET_ACTUAL_SETTINGS_HEADER) {
                        // byte accepted
                        temp_settings[state - 1] = rx;
                    }
                    else {
                        state = IDLE; 
                    }
                    break;                    
                case SET_H: 
                    // Saving the information about the incoming BME setting
                    if(rx == BME280_NO_OVERSAMPLING ||
                       rx == BME280_OVERSAMPLING_1X ||
                       rx == BME280_OVERSAMPLING_2X ||
                       rx == BME280_OVERSAMPLING_4X ||
                       rx == BME280_OVERSAMPLING_8X ||
                       rx == BME280_OVERSAMPLING_16X) {
                        temp_settings[state - 1] = rx; 
                        flag_hum_setting = 1;
                    } 
                    else {
                        flag_hum_setting = 0;
                    }
                    break;
                case SET_T: 
                    // Saving the information about the incoming BME setting
                    if(rx == BME280_NO_OVERSAMPLING ||
                       rx == BME280_OVERSAMPLING_1X ||
                       rx == BME280_OVERSAMPLING_2X ||
                       rx == BME280_OVERSAMPLING_4X ||
                       rx == BME280_OVERSAMPLING_8X ||
                       rx == BME280_OVERSAMPLING_16X) {
                        temp_settings[state - 1] = rx; 
                        flag_temp_setting = 1;
                    }  
                    else {
                        flag_temp_setting = 0;
                    }
                    break;
                case SET_P: 
                    // Saving the information about the incoming BME setting
                    if(rx == BME280_NO_OVERSAMPLING ||
                       rx == BME280_OVERSAMPLING_1X ||
                       rx == BME280_OVERSAMPLING_2X ||
                       rx == BME280_OVERSAMPLING_4X ||
                       rx == BME280_OVERSAMPLING_8X ||
                       rx == BME280_OVERSAMPLING_16X) {
                        temp_settings[state - 1] = rx; 
                        flag_press_setting = 1;
                    }  
                    else {
                        flag_press_setting = 0;
                    }
                    break;
                case SET_S: 
                    // Saving the information about the incoming BME setting
                    if(rx == BME280_TSTANBDY_0_5_MS ||
                       rx == BME280_TSTANBDY_62_5_MS ||
                       rx == BME280_TSTANBDY_125_MS ||
                       rx == BME280_TSTANBDY_250_MS ||
                       rx == BME280_TSTANBDY_500_MS ||
                       rx == BME280_TSTANBDY_1000_MS ||
                       rx == BME280_TSTANBDY_10_MS ||
                       rx == BME280_TSTANBDY_20_MS) {
                        temp_settings[state - 1] = rx; 
                        flag_sb_time_setting = 1;
                    }  
                    else {
                        flag_sb_time_setting = 0;
                    }
                    break;
                case SET_F: 
                    // Saving the information about the incoming BME setting
                    if(rx == BME280_FILTER_COEFF_OFF ||
                       rx == BME280_FILTER_COEFF_2 ||
                       rx == BME280_FILTER_COEFF_4 ||
                       rx == BME280_FILTER_COEFF_8 ||
                       rx == BME280_FILTER_COEFF_16) {
                        temp_settings[state - 1] = rx; 
                        flag_filt_coeff = 1;
                    }  
                    else {
                        flag_filt_coeff = 0;
                    }
                    break;
                case TAIL: 
                    if(rx == BME280_SET_ACTUAL_SETTINGS_TAIL) {
                        temp_settings[state - 1] = rx;
                        
                        // Communicate packet was acquired correctly
                        flag_new_setting_ready = 1;                        
                        state = IDLE;                        
                    }  
                    else {
                        for(int i=0;i<BME280_DEF_SETTING_PACKET;i++) {
                            temp_settings[i] = 0;
                        }
                        
                        flag_new_setting_ready  = 0;
                        flag_hum_setting        = 0;
                        flag_temp_setting       = 0;
                        flag_press_setting      = 0;
                        flag_sb_time_setting    = 0;
                        flag_filt_coeff         = 0;
                        
                        state = IDLE; 
                    }
                    break; 
                default: 
                    for(int i=0;i<BME280_DEF_SETTING_PACKET;i++) {
                            temp_settings[i] = 0;
                    }
                    
                    flag_new_setting_ready  = 0;
                    flag_hum_setting        = 0;
                    flag_temp_setting       = 0;
                    flag_press_setting      = 0;
                    flag_sb_time_setting    = 0;
                    flag_filt_coeff         = 0;
                    
                    state = IDLE;
                    break;                    
            } // end switch-case state            
            
        } // end if flag_rx
        
        
        // When we're not in IDLE or TAIL, we have a time window within which we can accept bytes
        if(state == HEAD || state == SET_H || state == SET_T || state == SET_P ||
           state == SET_S || state == SET_F) {
            if(flag_five_sec) {
                UART_PutString("WATCHDOG\r\n");
                flag_five_sec = 0;
                // 5s timeout has occurred. We have to discard data and get back to IDLE state
                for(int i=0;i<BME280_DEF_SETTING_PACKET;i++) {
                    temp_settings[i] = 0;
                }
                state = IDLE;
            }
        }
        
        
        // Handle ramp pattern
        if(flag_ramp_increment) {
            flag_200ms          = 0;
            flag_ramp_increment = 0;
            Mod_Ramp();
        } // end ramp pattern
        
        
        // Handle square pattern -> done directly in ISR
        
        
        // Handle sine pattern
        if(flag_sine_increment) {
            flag_200ms          = 0;
            flag_sine_increment = 0;
            Mod_Sine();
        }
        
        
        // Handle triangle pattern
        if(flag_trng_increment) {
            flag_200ms          = 0;
            flag_trng_increment = 0;
            Mod_Triangle();
        }
        
        
        // Handle square+triangle pattern
        if(flag_sqtr_increment) {
            flag_200ms          = 0;
            flag_sqtr_increment = 0;
            Mod_SquareTriangle();
        }
        
        
        // If the GUI wants to have the configuration of BME280
        if(flag_settings) {
            flag_settings = 0;
            // Communication of settings is allowed only if the streaming is disabled
            if(flag_stream == 0) {
                // Send BME280 settings buffer
                UART_PutArray(BME280_ActualSettings, BME280_DEF_SETTING_PACKET);
            }             
        }
        
        
        // If new BME280 setting was set from GUI
        if(flag_new_setting_ready) {
            flag_new_setting_ready = 0;
            
            if(flag_stream == 0) {
                
                // Humidity
                if(flag_hum_setting) {
                    flag_hum_setting = 0;
                    
                    error = BME280_SetHumidityOversampling(&bme280, temp_settings[1]);
                    //bme280.settings.osr_h = temp_settings[1];
                    if(error == BME280_OK) {                         
                        EEPROM_WriteByte(bme280.settings.osr_h, EEPROM_H_OSR);
                    }
                }
                else {
                    // if not valid, set default
                    error = BME280_SetHumidityOversampling(&bme280, BME280_OVERSAMPLING_1X);
                    //bme280.settings.osr_h = BME280_OVERSAMPLING_1X;
                    if(error == BME280_OK) {                         
                        EEPROM_WriteByte(bme280.settings.osr_h, EEPROM_H_OSR);
                    }
                }
                // Temperature
                if(flag_temp_setting) {
                    flag_temp_setting = 0;
                    
                    error = BME280_SetTemperatureOversampling(&bme280, temp_settings[2]);
                    //bme280.settings.osr_t = temp_settings[2];
                    if(error == BME280_OK) {                         
                        EEPROM_WriteByte(bme280.settings.osr_t, EEPROM_T_OSR);
                    }
                }
                else {
                    // if not valid, set default
                    error = BME280_SetTemperatureOversampling(&bme280, BME280_OVERSAMPLING_2X);
                    //bme280.settings.osr_t = BME280_OVERSAMPLING_2X;
                    if(error == BME280_OK) {                         
                        EEPROM_WriteByte(bme280.settings.osr_t, EEPROM_T_OSR);
                    }
                }
                // Pressure
                if(flag_press_setting) {
                    flag_press_setting = 0;
                    
                    error = BME280_SetPressureOversampling(&bme280, temp_settings[3]);
                    //bme280.settings.osr_p = temp_settings[3];
                    if(error == BME280_OK) {                         
                        EEPROM_WriteByte(bme280.settings.osr_p, EEPROM_P_OSR);
                    }
                }
                else {
                    // if not valid, set default
                    error = BME280_SetPressureOversampling(&bme280, BME280_OVERSAMPLING_16X);
                    //bme280.settings.osr_p = BME280_OVERSAMPLING_16X;
                    if(error == BME280_OK) {                         
                        EEPROM_WriteByte(bme280.settings.osr_p, EEPROM_P_OSR);
                    }
                }
                // Stand-by time
                if(flag_sb_time_setting) {
                    flag_sb_time_setting = 0;
                    
                    error = BME280_SetStandbyTime(&bme280, temp_settings[4]);
                    //bme280.settings.stanby_time = temp_settings[4];
                    if(error == BME280_OK) {                         
                        EEPROM_WriteByte(bme280.settings.stanby_time, EEPROM_SB_TIME);
                    }
                }
                else {
                    // if not valid, set default
                    error = BME280_SetStandbyTime(&bme280, BME280_TSTANBDY_0_5_MS);
                    //bme280.settings.stanby_time = BME280_TSTANBDY_0_5_MS;
                    if(error == BME280_OK) {                         
                        EEPROM_WriteByte(bme280.settings.stanby_time, EEPROM_SB_TIME);
                    }
                }
                // Filter coefficient
                if(flag_filt_coeff) {
                    flag_filt_coeff = 0;
                    
                    error = BME280_SetIIRFilter(&bme280, temp_settings[5]);
                    //bme280.settings.filter = temp_settings[5];
                    if(error == BME280_OK) {                         
                        EEPROM_WriteByte(bme280.settings.filter, EEPROM_FILT);
                    }
                }
                else {
                    // if not valid, set default
                    error = BME280_SetIIRFilter(&bme280, BME280_FILTER_COEFF_16);
                    //bme280.settings.filter = BME280_FILTER_COEFF_16;
                    if(error == BME280_OK) {                         
                        EEPROM_WriteByte(bme280.settings.filter, EEPROM_FILT);
                    }
                }
                
                BME280_ActualSettings[0]                             = BME280_ACTUAL_SETTINGS_HEADER;
                BME280_ActualSettings[1]                             = EEPROM_ReadByte(EEPROM_H_OSR);
                BME280_ActualSettings[2]                             = EEPROM_ReadByte(EEPROM_T_OSR);
                BME280_ActualSettings[3]                             = EEPROM_ReadByte(EEPROM_P_OSR);
                BME280_ActualSettings[4]                             = EEPROM_ReadByte(EEPROM_SB_TIME);
                BME280_ActualSettings[5]                             = EEPROM_ReadByte(EEPROM_FILT);
                BME280_ActualSettings[BME280_DEF_SETTING_PACKET - 1] = BME280_ACTUAL_SETTINGS_TAIL;
                
                UART_PutArray(BME280_ActualSettings, BME280_DEF_SETTING_PACKET);
                
            }
            
        }
        
        
        // Send data
        if(flag_stream) {

            // Blocking the execution while the flag_read_gas = 1
            while(flag_read_data == 0);
            
            // Data bundling 
            BundleData(&gas_sensor, &bme280); 
            
            // Output-Voltage gas sensor & BME280 data transmitting
            UART_PutArray(GlobalBuffer, DATA_BUFFER_SIZE);
            
            // Trasmission completed, reset flags
            flag_read_gas  = 0;
            flag_read_bme  = 0; 
            flag_read_data = 0; 
            
        } // end data streaming
        
    } // end for loop
} // end main

/* [] END OF FILE */
