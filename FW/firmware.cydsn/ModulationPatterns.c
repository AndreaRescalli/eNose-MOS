/**
 *
 * \file  ModulationPatterns.c
 * \brief Source file in charge of handling heater modulation patterns.
 *
 * \author Andrea Rescalli
 * \date   05/05/2023
 *
 */


#include "ModulationPatterns.h"


/**
 * \brief Function that adjusts the PWM compare value to change duty cycle for ramp pattern.
 *
 * \param[in] void
 * \return void
*/
void Mod_Ramp(void) {    
    // read the actual cmp value (they are all equal)
    uint8_t cmp = PWM_AS_HC_ReadCompare1();
    
    // if it is different than 0, decrement by 11 (we do a 11% increment every 30s)
    if(cmp) {
        Control_Reg_KILL_PWM_Write(ENABLE_PWM);
        cmp -= 11;
        // S4
        PWM_S4_HC_12_WriteCompare1(cmp);
        PWM_S4_HC_12_WriteCompare2(cmp);
        PWM_S4_HC_34_WriteCompare1(cmp);
        PWM_S4_HC_34_WriteCompare2(cmp);
        // S6
        PWM_S6_HC_WriteCompare1(cmp);
        PWM_S6_HC_WriteCompare2(cmp);
        // AS
        PWM_AS_HC_WriteCompare1(cmp);
        PWM_AS_HC_WriteCompare2(cmp);
    }
    // if it is 0 we need to set it to the highest value which is PWM_PERIOD
    else {
        // Disable output so that it is 0V, otherwise at CMP = 99 the duty cycle is not 0
        Control_Reg_KILL_PWM_Write(DISABLE_PWM);
        // S4
        PWM_S4_HC_12_WriteCompare1(PWM_PERIOD);
        PWM_S4_HC_12_WriteCompare2(PWM_PERIOD);
        PWM_S4_HC_34_WriteCompare1(PWM_PERIOD);
        PWM_S4_HC_34_WriteCompare2(PWM_PERIOD);
        // S6
        PWM_S6_HC_WriteCompare1(PWM_PERIOD);
        PWM_S6_HC_WriteCompare2(PWM_PERIOD);
        // AS
        PWM_AS_HC_WriteCompare1(PWM_PERIOD);
        PWM_AS_HC_WriteCompare2(PWM_PERIOD);
    }
    
    /*
    cmp = PWM_AS_HC_ReadCompare1();
    char msg[50] = {0};
    sprintf(msg, "cmp: %d\r\n",cmp);
    UART_PutString(msg);
    */
    
} // end Mod_Ramp



/**
 * \brief Function that adjusts the PWM compare value to change duty cycle for sine pattern.
 *
 * \param[in] void
 * \return void
*/
void Mod_Sine(void) {
    
    sine_dc = sine_table[lut_idx];
    
    if(sine_dc == 0) {
        // Disable output so that it is 0V
        Control_Reg_KILL_PWM_Write(DISABLE_PWM);
    }
    else {
        Control_Reg_KILL_PWM_Write(ENABLE_PWM);
        if(sine_dc > 99) {
            // When DC has to be 100, we need to write 0 but PWM_PERDIOD is 99. Force 0 to not have sine_cmp overflow
            sine_cmp = 0;
        }
        else {
            sine_cmp = PWM_PERIOD-sine_dc;
        }
        // S4
        PWM_S4_HC_12_WriteCompare1(sine_cmp);
        PWM_S4_HC_12_WriteCompare2(sine_cmp);
        PWM_S4_HC_34_WriteCompare1(sine_cmp);
        PWM_S4_HC_34_WriteCompare2(sine_cmp);
        // S6
        PWM_S6_HC_WriteCompare1(sine_cmp);
        PWM_S6_HC_WriteCompare2(sine_cmp);
        // AS
        PWM_AS_HC_WriteCompare1(sine_cmp);
        PWM_AS_HC_WriteCompare2(sine_cmp);
    }
    
    /*
    char msg[50] = {0};
    sprintf(msg, "dc: %d | cmp: %d\r\n", sine_dc, sine_cmp);
    UART_PutString(msg);
    */
    
    // lut_idx is incremented by 1 on each ISR call and then 
    // wrapped around to 0 when it reaches the end of the lookup table
    // using the modulo operator. 50 is the length of the sine lookup table.
    lut_idx = (lut_idx + 1) % 50;
    
} // end Mod_Sine



/**
 * \brief Function that adjusts the PWM compare value to change duty cycle for triangle pattern.
 *
 * \param[in] void
 * \return void
*/
void Mod_Triangle(void) {
    // read the actual cmp value (they are all equal)
    uint8_t cmp = PWM_AS_HC_ReadCompare1();

    if(trng_state == UP) {
        if(cmp) {
            if(cmp == 1) {
                // Turnaround, so increment and move to DOWN
                Control_Reg_KILL_PWM_Write(ENABLE_PWM);
                cmp += 2;
                // S4
                PWM_S4_HC_12_WriteCompare1(cmp);
                PWM_S4_HC_12_WriteCompare2(cmp);
                PWM_S4_HC_34_WriteCompare1(cmp);
                PWM_S4_HC_34_WriteCompare2(cmp);
                // S6
                PWM_S6_HC_WriteCompare1(cmp);
                PWM_S6_HC_WriteCompare2(cmp);
                // AS
                PWM_AS_HC_WriteCompare1(cmp);
                PWM_AS_HC_WriteCompare2(cmp);
                
                trng_state = DOWN;
            }
            else {
                // Decrement cmp by 2 every second to increment dc by 2 every second and reach 100% in 50s
                Control_Reg_KILL_PWM_Write(ENABLE_PWM);
                cmp -= 2;
                // S4
                PWM_S4_HC_12_WriteCompare1(cmp);
                PWM_S4_HC_12_WriteCompare2(cmp);
                PWM_S4_HC_34_WriteCompare1(cmp);
                PWM_S4_HC_34_WriteCompare2(cmp);
                // S6
                PWM_S6_HC_WriteCompare1(cmp);
                PWM_S6_HC_WriteCompare2(cmp);
                // AS
                PWM_AS_HC_WriteCompare1(cmp);
                PWM_AS_HC_WriteCompare2(cmp);
            }
        }
        // if it is 0 we need to set it to the highest value which is PWM_PERIOD
        else {
            // Disable output so that it is 0V, otherwise at CMP = 99 the duty cycle is not 0
            Control_Reg_KILL_PWM_Write(DISABLE_PWM);
            // S4
            PWM_S4_HC_12_WriteCompare1(PWM_PERIOD);
            PWM_S4_HC_12_WriteCompare2(PWM_PERIOD);
            PWM_S4_HC_34_WriteCompare1(PWM_PERIOD);
            PWM_S4_HC_34_WriteCompare2(PWM_PERIOD);
            // S6
            PWM_S6_HC_WriteCompare1(PWM_PERIOD);
            PWM_S6_HC_WriteCompare2(PWM_PERIOD);
            // AS
            PWM_AS_HC_WriteCompare1(PWM_PERIOD);
            PWM_AS_HC_WriteCompare2(PWM_PERIOD);
        }
        
        /*
        cmp = PWM_AS_HC_ReadCompare1();
        char msg[50] = {0};
        sprintf(msg, "cmp: %d\r\n", cmp);
        UART_PutString(msg);
        */
        
    } // end UP
    else {
        if(cmp == 97) {
            // Disable output so that it is 0V, otherwise at CMP = 99 the duty cycle is not 0
            Control_Reg_KILL_PWM_Write(DISABLE_PWM);
            // S4
            PWM_S4_HC_12_WriteCompare1(PWM_PERIOD);
            PWM_S4_HC_12_WriteCompare2(PWM_PERIOD);
            PWM_S4_HC_34_WriteCompare1(PWM_PERIOD);
            PWM_S4_HC_34_WriteCompare2(PWM_PERIOD);
            // S6
            PWM_S6_HC_WriteCompare1(PWM_PERIOD);
            PWM_S6_HC_WriteCompare2(PWM_PERIOD);
            // AS
            PWM_AS_HC_WriteCompare1(PWM_PERIOD);
            PWM_AS_HC_WriteCompare2(PWM_PERIOD);
        }
        else if(cmp == PWM_PERIOD) {
            // Turnaround, so decrement and move to UP
            Control_Reg_KILL_PWM_Write(ENABLE_PWM);
            cmp -= 2;
            // S4
            PWM_S4_HC_12_WriteCompare1(cmp);
            PWM_S4_HC_12_WriteCompare2(cmp);
            PWM_S4_HC_34_WriteCompare1(cmp);
            PWM_S4_HC_34_WriteCompare2(cmp);
            // S6
            PWM_S6_HC_WriteCompare1(cmp);
            PWM_S6_HC_WriteCompare2(cmp);
            // AS
            PWM_AS_HC_WriteCompare1(cmp);
            PWM_AS_HC_WriteCompare2(cmp);
            
            trng_state = UP;
        }
        else {
            // Increment cmp by 2 every second to decrement dc by 2 every second and reach 0% in 50s
            Control_Reg_KILL_PWM_Write(ENABLE_PWM);
            cmp += 2;
            // S4
            PWM_S4_HC_12_WriteCompare1(cmp);
            PWM_S4_HC_12_WriteCompare2(cmp);
            PWM_S4_HC_34_WriteCompare1(cmp);
            PWM_S4_HC_34_WriteCompare2(cmp);
            // S6
            PWM_S6_HC_WriteCompare1(cmp);
            PWM_S6_HC_WriteCompare2(cmp);
            // AS
            PWM_AS_HC_WriteCompare1(cmp);
            PWM_AS_HC_WriteCompare2(cmp);
        }
        
        /*
        cmp = PWM_AS_HC_ReadCompare1();    
        char msg[50] = {0};
        sprintf(msg, "cmp: %d\r\n", cmp);
        UART_PutString(msg);
        */
            
    } // end DOWN
    
} // end Mod_Triangle



/**
 * \brief Function that adjusts the PWM compare value to change duty cycle for square+triangle pattern.
 *
 * \param[in] void
 * \return void
*/
void Mod_SquareTriangle(void) {
    
    sqtr_dc = sqtr_table[lut_sqtr_idx];
    
    if(sqtr_dc == 0) {
        // Disable output so that it is 0V
        Control_Reg_KILL_PWM_Write(DISABLE_PWM);
    }
    else {
        Control_Reg_KILL_PWM_Write(ENABLE_PWM);
        if(sqtr_dc > 99) {
            // When DC has to be 100, we need to write 0 but PWM_PERDIOD is 99. Force 0 to not have sine_cmp overflow
            sqtr_cmp = 0;
        }
        else {
            sqtr_cmp = PWM_PERIOD-sqtr_dc;
        }
        // S4
        PWM_S4_HC_12_WriteCompare1(sqtr_cmp);
        PWM_S4_HC_12_WriteCompare2(sqtr_cmp);
        PWM_S4_HC_34_WriteCompare1(sqtr_cmp);
        PWM_S4_HC_34_WriteCompare2(sqtr_cmp);
        // S6
        PWM_S6_HC_WriteCompare1(sqtr_cmp);
        PWM_S6_HC_WriteCompare2(sqtr_cmp);
        // AS
        PWM_AS_HC_WriteCompare1(sqtr_cmp);
        PWM_AS_HC_WriteCompare2(sqtr_cmp);
    }
    
    /*
    char msg[50] = {0};
    sprintf(msg, "dc: %d | cmp: %d\r\n", sqtr_dc, sqtr_cmp);
    UART_PutString(msg);
    */    
    
    // lut_sqtr_idx is incremented by 1 on each ISR call and then 
    // wrapped around to 0 when it reaches the end of the lookup table
    // using the modulo operator. 100 is the length of the square+triangle lookup table.
    lut_sqtr_idx = (lut_sqtr_idx + 1) % 100;

} // end Mod_SquareTriangle

/* [] END OF FILE */
