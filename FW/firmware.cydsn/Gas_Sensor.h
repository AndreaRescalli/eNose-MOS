/* ========================================
 *
 * \file  Gas_Sensor.c
 * \brief This header file contains definition of structs to handle data of gas sensors
 *
 * \author Davide Marzorati, Damiano Rosario Tasso, Andrea Rescalli
 * \date   07/05/2023
 *
 */
#ifndef __GAS_SENSORS_H__
    #define __GAS_SENSORS_H__
    
    #include "project.h"
    
    /******************************************/
    /*              Typedefs                  */
    /******************************************/
    /*
    *   Gas Sensor voltage 
    */
    typedef struct{
        int32 S4_1_v;       ///< Voltage detected by S4_1 gas sensor
        int32 S4_2_v;       ///< Voltage detected by S4_2 gas sensor
        int32 S4_3_v;       ///< Voltage detected by S4_3 gas sensor
        int32 S4_4_v;       ///< Voltage detected by S4_4 gas sensor
        int32 S6_1_v;       ///< Voltage detected by S6_1 gas sensor
        int32 S6_2_v;       ///< Voltage detected by S6_2 gas sensor
        int32 AS_1_v;       ///< Voltage detected by AM_1 gas sensor
        int32 AS_2_v;       ///< Voltage detected by AM_s gas sensor
    }Gas_Sens_Voltage;
    
    /*
    *   Gas Sensor heater voltage 
    */
    typedef struct{
        int32 S4_1_h;       ///< Voltage detected by S4_1 gas sensor
        int32 S4_2_h;       ///< Voltage detected by S4_2 gas sensor
        int32 S4_3_h;       ///< Voltage detected by S4_3 gas sensor
        int32 S4_4_h;       ///< Voltage detected by S4_4 gas sensor
        int32 S6_1_h;       ///< Voltage detected by S6_1 gas sensor
        int32 S6_2_h;       ///< Voltage detected by S6_2 gas sensor
        int32 AS_1_h;       ///< Voltage detected by AM_1 gas sensor
        int32 AS_2_h;       ///< Voltage detected by AM_s gas sensor
    }Gas_Sens_Voltage_H;
    
    /*
    *   Gas Sensor general structure
    */
    typedef struct{
        Gas_Sens_Voltage    Gas_Volt_Data;     ///< Gas sensors voltage data
    }Gas_Sensor;
    
    Gas_Sensor gas_sensor; 
    
    int32 S4_1_v;       ///< Voltage detected by S4_1 gas sensor
    int32 S4_2_v;       ///< Voltage detected by S4_2 gas sensor
    int32 S4_3_v;       ///< Voltage detected by S4_3 gas sensor
    int32 S4_4_v;       ///< Voltage detected by S4_4 gas sensor
    int32 S6_1_v;       ///< Voltage detected by S6_1 gas sensor
    int32 S6_2_v;       ///< Voltage detected by S6_2 gas sensor
    int32 AS_1_v;       ///< Voltage detected by AM_1 gas sensor
    int32 AS_2_v;       ///< Voltage detected by AM_s gas sensor
    
#endif
/* [] END OF FILE */
