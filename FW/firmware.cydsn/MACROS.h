/**
 *
 * \file  MACROS.h
 * \brief Header file containing system-level defines and global variables.
 *
 * \author Andrea Rescalli
 * \date   05/05/2023
 *
 */

#ifndef __MACROS_H_
    #define __MACROS_H_
    
    // =============================================
    //                   INCLUDES
    // =============================================
    #include "cytypes.h"

    
    
    // =============================================
    //               GLOBALS & FLAGS
    // ============================================= 
    #define TIMER_PERIOD        200     ///< 200 ms
    #define TIMER_PERIOD_ADC    100     ///< 100 ms
    #define TIMER_PERIOD_WTD    250     ///< 250 ms
    #define PWM_PERIOD          99      ///< 25  us
    #define DISABLE_PWM         1       ///< Disable PWM output through control register
    #define ENABLE_PWM          0       ///< Enable  PWM output through control register
    
    #define UP                  1       ///< Rising part of triangle pattern
    #define DOWN                0       ///< Falling part of triangle pattern
    
    #define HIGH                1       ///< Logic state for hydraulic management
    #define LOW                 0       ///< Logic state for hydraulic management
    
    #define IDLE                0       ///< IDLE state for incoming packet handling
    #define HEAD                1       ///< Read-HEAD state for incoming packet handling
    #define SET_H               2       ///< Read-hum state for incoming packet handling
    #define SET_T               3       ///< Read-temp state for incoming packet handling
    #define SET_P               4       ///< Read-press state for incoming packet handling
    #define SET_S               5       ///< Read-st state for incoming packet handling
    #define SET_F               6       ///< Read-filt state for incoming packet handling
    #define TAIL                7       ///< Read-TAIL state for incoming packet handling
    
    #define DATA_HEADER         0xAA    ///< Header for data packet
    #define DATA_TAIL           0xF0    ///< Tail for data packet
    #define DATA_GAS_ENV_SIZE   44      ///< Gas sensors output voltages + BME environmental variables
    #define DATA_BUFFER_SIZE    1+1+DATA_GAS_ENV_SIZE+1
    // Mask to split 32bit data
    #define MSB                 0xFF000000
    #define CSB1                0x00FF0000
    #define CSB2                0x0000FF00
    #define LSB                 0x000000FF
    
    // Macro for MUX output selection
    #define AMUX_VOUT_1         0
    #define A_OUT               1
    #define A_MUX_VOUT_2        2

    uint8_t pwm_cmp_value;                  ///< Initially the heater has to be fully activated so cmp to 0
    uint8_t state;                          ///< Variaible to keep track of packet reading state
    uint8_t GlobalBuffer[DATA_BUFFER_SIZE]; ///< Buffer containing data to be sent @100Hz to GUI
    
#endif

/* [] END OF FILE */
