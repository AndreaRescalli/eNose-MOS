/**
 *
 * \file  Interrupts.c
 * \brief Source file in charge of handling interrupt routines.
 *
 * \author Andrea Rescalli
 * \date   05/05/2023
 *
 */

#include "Interrupts.h"
#include <stdio.h>


/**
 * \brief UART ISR.
 * 
 * ISR of the UART that is used to pilot remotely the device based on commands recieved.
*/
CY_ISR(Custom_ISR_RX) {
    
    // Check UART status
    if(UART_ReadRxStatus() == UART_RX_STS_FIFO_NOTEMPTY) {
        // If we have recieved a byte, communicate it
        flag_rx = 1;
    }    
    
} // end ISR_RX



/**
 * \brief Timer ISR triggered every 200ms.
*/
CY_ISR(Custom_ISR_TIMER200ms) {
    
    // Read timer status to bring interrupt line low
    Timer200ms_ReadStatusRegister();
    
    flag_200ms      = 1;
    counter        += 1;
    
    // Every second -> handle sine, triangle
    if((counter%5) == 0) {
        if(flag_stream) {
            if(flag_enable_sine) {
                flag_sine_increment  = 1;
            }
            else if(flag_enable_triangle) {
                flag_trng_increment  = 1;
            }
            else if(flag_enable_sqtr) {
                flag_sqtr_increment  = 1;
            }
        }
    }
    
    // Every 30s -> handle ramp and square
    if((counter%150) == 0) {
        if(counter == 1500) {
            counter = 0;
            //flag_enable_ramp       = 0;
            //flag_enable_square     = 0;
            //flag_enable_sine       = 0;
            //flag_enable_triangle   = 0;
            //flag_enable_sqtr       = 0;
        }
        if(flag_stream) {
            if(flag_enable_ramp) {
                flag_ramp_increment  = 1;
            }
            else if(flag_enable_square) {
                if(counter == 0) {
                    // Start high
                    //UART_PutString("t0\r\n");
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
                }
                else {
                    // Toggle output
                    //UART_PutString("+30s\r\n");
                    Control_Reg_KILL_PWM_Write(!Control_Reg_KILL_PWM_Read());
                }
            }
        }
    }    
    
} // end ISR_TIMER200ms



/**
 * \brief Watchdog ISR triggered every 250ms.
*/
CY_ISR(Custom_ISR_WATCHDOG) {
    
    // Read timer status to bring interrupt line low
    Watchdog_ReadStatusRegister();
    
    // We have an ISR each 250ms but we want an alarm each 5s
    counter_wtd++;
    
    // When 5 sec have passed
    if (counter_wtd == 20) {
        flag_five_sec = 1;
        counter_wtd = 0;
    }
       
} // end ISR_WATCHDOG



/**
 * \brief TimerADC ISR triggered every 10ms.
*/
CY_ISR(Custom_ISR_ADC) {
    
    // Read timer status to bring interrupt line low
    TimerADC_ReadStatusRegister();
    
    // Gas Sensor data smapling
    Internal_MUX_Select(A_OUT);
    
    // Reading S4_1 and S4_3
    MuxSelection(&gas_sensor, 0);
    
    // Reading AS_1 and S6_2
    MuxSelection(&gas_sensor, 2);
    
    // Reading S6_1 and S4_4
    MuxSelection(&gas_sensor, 4);
    
    // Reading S4_2 and AS_2
    MuxSelection(&gas_sensor, 6);  
    
    // Reading flag state: HIGH
    flag_read_gas = 1; 
    
    // BME280 data smapling
    BME280_ErrorCode error = BME280_ReadData(&bme280, BME280_ALL_COMP);
    
    if (error == BME280_OK) {
        flag_read_bme = 1; 
    }
//    else {
//        flag_read_bme = LOW;
//        BME280_Reset(&bme280);    
//    }
    
    // flag check to prepare the correct data trasmission!
    if((flag_read_gas) && (flag_read_bme)) {
        flag_read_data = 1; 
    }
    
} // end ISR_ADC



/**
 * \brief Function that resets the timer.
 *
 * \param[in] void
 * \return void
*/
void Reset_TIMER(void) {
    
    // Reset the timer200ms
    Timer200ms_Stop();
    Timer200ms_WriteCounter(TIMER_PERIOD-1);
    Timer200ms_Enable();
    flag_200ms  = 0;
    
    // Reset pettern-specific variables
    counter             = -1;
    flag_ramp_increment = 0;
    flag_sine_increment = 0;
    lut_idx             = 0;
    flag_trng_increment = 0;
    trng_state          = UP;
    lut_sqtr_idx        = 0;
    flag_sqtr_increment = 0;
    
    // Reset the ADC timer
    TimerADC_Stop();
    TimerADC_WriteCounter(TIMER_PERIOD_ADC-1);
    TimerADC_Enable();
    flag_read_gas       = 0;
    flag_read_bme       = 0;
    flag_read_data      = 0;
    
} // end Reset_TIMER



void Reset_WatchdogTimer(void) {
    
    // Reset the timer
    Watchdog_Stop();
    Watchdog_WriteCounter(TIMER_PERIOD_WTD-1);
    Watchdog_Enable();
    counter_wtd = 0;
    flag_five_sec = 0; 
    
} // end Reset_WatchdogTimer


/* [] END OF FILE */
