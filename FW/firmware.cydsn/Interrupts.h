/**
 *
 * \file  Interrupts.h
 * \brief Header file in charge of handling interrupt routines.
 *
 * \author Andrea Rescalli
 * \date   05/05/2023
 *
 */


#ifndef __INTERRUPTS_H_
    #define __INTERRUPTS_H_
    
    // =============================================
    //                   INCLUDES
    // =============================================
    #include "cytypes.h"
    #include "MACROS.h"
    #include "project.h"
    #include "ModulationPatterns.h"
    #include "mux_functions.h"
    
    
    
    // =============================================
    //               GLOBALS & FLAGS
    // ============================================= 
    volatile uint8_t flag_rx;               ///< Flag that tells a byte has been recieved
    volatile uint8_t flag_stream;           ///< Flag that activates streaming and sensors modulation
    volatile uint8_t flag_enable_ramp;      ///< Flag that enables ramp modulation pattern
    volatile uint8_t flag_enable_square;    ///< Flag that enables square modulation pattern
    volatile uint8_t flag_enable_sine;      ///< Flag that enables sine modulation pattern
    volatile uint8_t flag_enable_triangle;  ///< Flag that enables triangle modulation pattern
    volatile uint8_t flag_enable_sqtr;      ///< Flag that enables square+triangle modulation pattern
    
    volatile uint8_t flag_200ms;            ///< Flag that tells 200ms have passed
    volatile uint8_t flag_ramp_increment;   ///< Flag that tells it's time to increment duty cycle of pwm for ramp
    volatile uint8_t flag_sine_increment;   ///< Flag that tells it's time to increment duty cycle of pwm for sine
    volatile uint8_t flag_trng_increment;   ///< Flag that tells it's time to increment duty cycle of pwm for triangle
    volatile uint8_t flag_sqtr_increment;   ///< Flag that tells it's time to increment duty cycle of pwm for square+triangle
    volatile int16_t counter;               ///< Counter to keep track of each timer overflow
    
    volatile uint8_t flag_five_sec;         ///< Flag for watchdog timer on BME280 settings packet
    volatile int16_t counter_wtd;           ///< Counter to keep track of each watchdog timer overflow
    
    volatile uint8_t flag_read_gas;         ///< Flag that tells gas data have been acquired
    volatile uint8_t flag_read_bme;         ///< Flag that tells BME data have been acquired
    volatile uint8_t flag_read_data;        ///< Flag that tells all data have been acquired
    
    
    
    // =============================================
    //                  FUNCTIONS
    // =============================================  
    /**
     * \brief UART ISR.
     * 
     * ISR of the UART that is used to pilot remotely the device based on commands recieved.
    */    
    CY_ISR_PROTO(Custom_ISR_RX);
    
    
    /**
     * \brief Timer ISR triggered every 200ms.
    */
    CY_ISR_PROTO(Custom_ISR_TIMER200ms);
    
    
    /**
     * \brief Watchdog ISR triggered every 250ms.
    */
    CY_ISR_PROTO(Custom_ISR_WATCHDOG);
    
    
    /**
     * \brief TimerADC ISR triggered every 100ms.
    */
    CY_ISR_PROTO(Custom_ISR_ADC);
    
    
    /**
     * \brief Function that resets the timer.
     *
     * \param[in] void
     * \return void
    */
    void Reset_TIMER(void);
    
    
    /**
     * \brief Function that resets the Watchdog timer.
     *
     * \param[in] void
     * \return void
    */
    void Reset_WatchdogTimer(void);
    
    
    
#endif

/* [] END OF FILE */
