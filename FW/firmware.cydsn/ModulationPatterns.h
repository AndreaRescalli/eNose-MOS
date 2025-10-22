/**
 *
 * \file  ModulationPatterns.h
 * \brief Header file in charge of handling heater modulation patterns.
 *
 * \author Andrea Rescalli
 * \date   05/05/2023
 *
 */

#ifndef __MODULATIONPATTERNS_H_
    #define __MODULATIONPATTERNS_H_
    
    // =============================================
    //                   INCLUDES
    // =============================================
    #include "cytypes.h"
    #include "MACROS.h"
    #include "project.h"
    #include <stdio.h>
    
    
    
    // =============================================
    //               GLOBALS & FLAGS
    // =============================================
    #define RAMP_PERIOD 300     ///< 5 min
    
    static const uint8_t sine_table[50] = {
        50, 56, 62, 68, 74, 78, 84, 88, 92, 96,
        98, 100, 100, 100, 100, 98, 96, 92, 88, 84, 
        78, 74, 68, 62, 56, 50, 44, 38, 32, 26, 
        22, 16, 12, 8, 4, 2, 0, 0, 0, 0, 
        2, 4, 8, 12, 16, 22, 26, 32, 38, 44
    }; ///< Look-up table to build a sine wave with PWM.
    volatile uint8_t sine_dc;       ///< Duty cycle value for PWM to have a sinusoidal pattern
    volatile uint8_t sine_cmp;      ///< Compare value value for PWM to get sine_dc
    volatile uint8_t lut_idx;       ///< Index variable to scroll the lut
    
    volatile uint8_t trng_state;    ///< State of the triangle wave (rising or falling)
    
    static const uint8_t sqtr_table[100] = {
        100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
        100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
        100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
        100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
        100, 100, 100, 100, 100, 100, 100, 100, 100, 0,
        4, 8, 12, 16, 20, 24, 28, 32, 36, 40,
        44, 48, 52, 56, 60, 64, 68, 72, 76, 80,
        84, 88, 92, 96, 100,
        96, 92, 88, 84, 80,
        76, 72, 68, 64, 60, 56, 52, 48, 44, 40,
        36, 32, 28, 24, 20, 16, 12, 8, 4, 0
    }; ///< Look-up table to build a square+triangle wave with PWM.
    volatile uint8_t sqtr_dc;       ///< Duty cycle value for PWM to have a square+triangle waveform
    volatile uint8_t sqtr_cmp;      ///< Compare value value for PWM to get sqtr_dc
    volatile uint8_t lut_sqtr_idx;  ///< Index variable to scroll the lut
    
    
    // =============================================
    //                  FUNCTIONS
    // =============================================
    /**
     * \brief Function that adjusts the PWM compare value to change duty cycle for ramp pattern.
     *
     * \param[in] void
     * \return void
    */
    void Mod_Ramp(void);
    
    
    /**
     * \brief Function that adjusts the PWM compare value to change duty cycle for sine pattern.
     *
     * \param[in] void
     * \return void
    */
    void Mod_Sine(void);
    
    
    /**
     * \brief Function that adjusts the PWM compare value to change duty cycle for triangle pattern.
     *
     * \param[in] void
     * \return void
    */
    void Mod_Triangle(void);
    
    
    /**
     * \brief Function that adjusts the PWM compare value to change duty cycle for square+triangle pattern.
     *
     * \param[in] void
     * \return void
    */
    void Mod_SquareTriangle(void);
    
#endif

/* [] END OF FILE */
