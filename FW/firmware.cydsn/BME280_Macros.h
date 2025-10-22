/**
 *
 * \file  BME280_Macros.h
 * \brief This header file contains defines to interface with a BME280 sensor.
 *
 * The development of these funtions was taken by 
 * https://github.com/dado93/PSoC-Example-Projects/tree/master/BME280/01-BME280.cydsn
 * and modified ad-hoc for this project.
 *
 * \author Davide Marzorati, Damiano Rosario Tasso, Andrea Rescalli
 * \date   07/05/2023
 *
 */


#ifndef __BME280_MACROS_H__
    #define __BME280_MACROS_H__
    
    #include "cytypes.h"
    #include "BME280_ErrorCodes.h"
    #include "BME280_I2C_Interface.h"
    #include "BME280_RegMap.h"
    #include "EEPROM.h"
    
    /************]*********************************************/
    /*        Useful buffering macros and variables           */
    /**********************************************************/
    #define BME280_DEF_SETTING_SIZE             5
    #define BME280_DEF_SETTING_PACKET           1+BME280_DEF_SETTING_SIZE+1
    #define BME280_RX_SETTINGS_BYTES            3
    #define BME280_RX_NEW_SETTING_BYTE          1
    #define BME280_SETTINGS_PACKET              1+BME280_RX_NEW_SETTING_BYTE+1
    #define BME280_SET_ACTUAL_SETTINGS_HEADER   't'
    #define BME280_SET_ACTUAL_SETTINGS_TAIL     'T'
    #define BME280_ACTUAL_SETTINGS_HEADER       0xBB
    #define BME280_ACTUAL_SETTINGS_TAIL         0xB0
    #define BME280_SETTING_TAIL                 0xD0
    #define HUM_OVERSAMPLING_HEADER             0xD1
    #define TEMP_OVERSAMPLING_HEADER            0xD2
    #define PRESS_OVERSAMPLING_HEADER           0xD3
    #define SB_TIME_HEADER                      0xD4
    #define FILT_COEFF_HEADER                   0xD5
    
    uint8 BME280_ActualSettings[BME280_DEF_SETTING_PACKET];
    uint8 BME280_SettingsBuffer[BME280_SETTINGS_PACKET];
    
    volatile uint8_t flag_settings;             ///< Flag to send BME default settings to GUI
    volatile uint8_t flag_new_setting_ready;    ///< Flag to set new settings coming from GUI
    volatile uint8_t flag_hum_setting;          ///< Flag to set humidity oversampling 
    volatile uint8_t flag_temp_setting;         ///< Flag to set temperature oversampling     
    volatile uint8_t flag_press_setting;        ///< Flag to set pressure oversampling     
    volatile uint8_t flag_sb_time_setting;      ///< Flag to set stanby time 
    volatile uint8_t flag_filt_coeff;           ///< Flag to set filter coefficient 
    
    
    /******************************************/
    /*              Macros                    */
    /******************************************/
        
    /**     
    *   EEPROM  
    *   Addresses in which was saved the defalut BME280 settings
    *   and where the new ones will be saved
    */
    #ifndef EEPROM_H_OSR
        #define EEPROM_H_OSR    0x0000
    #endif
    
    #ifndef EEPROM_T_OSR
        #define EEPROM_T_OSR    0x0001
    #endif
    
    #ifndef EEPROM_P_OSR
        #define EEPROM_P_OSR    0x0002
    #endif
    
    #ifndef EEPROM_SB_TIME
        #define EEPROM_SB_TIME  0x0003
    #endif
    
    #ifndef EEPROM_FILT
        #define EEPROM_FILT     0x0004
    #endif
    
    #endif
    
    /**
    *   WHO AM I value for the BME280 Sensor.
    *   
    *   This is the value that should be returned when reading
    *   the #BME280_WHO_AM_I_REG_ADDR. It can be used to check: 
    *   - if the device is working
    *   - the I2C communication
    */
    #ifndef BME280_WHO_AM_I
        #define BME280_WHO_AM_I 0x60
    #endif
    
    /**
    *   Macro for pressure compensation selection
    */
    #ifndef BME280_PRESS_COMP
        #define BME280_PRESS_COMP 1
    #endif
    
    /**
    *   Macro for temprature compensation selection
    */
    #ifndef BME280_TEMP_COMP
        #define BME280_TEMP_COMP 1 << 1
    #endif
    
    /**
    *   Macro for humidity compensation selection
    */
    #ifndef BME280_HUM_COMP
        #define BME280_HUM_COMP 1 << 2
    #endif
    
    /**
    *   Macro for compensation selection
    *
    *   This macro can be used to the compensation of the all 
    *   (temperature, pressure, and humidity) data.
    */
    #ifndef BME280_ALL_COMP
        #define BME280_ALL_COMP 0x07
    #endif
    
    /**
    *   Macro for status register check
    */
    #ifndef BM280_STATUS_IM_UPDATE
        #define BME280_STATUS_IM_UPDATE 0x01
    #endif
    
    /**
    *   I2C Address.
    */
    #ifndef BME280_I2C_ADDRESS
        #define BME280_I2C_ADDRESS 0x76
    #endif

    /**
    *   Byte to write on the reset register.
    */
    #ifndef BME280_RESET_COMMAND
        #define BME280_RESET_COMMAND 0xB6
    #endif

    /**
    *   Device sleep mode bit settings.
    */
    #ifndef BME280_SLEEP_MODE
        #define BME280_SLEEP_MODE 0x00
    #endif

    /**
    *   Device force mode bit settings.
    */
    #ifndef BME280_FORCED_MODE
        #define BME280_FORCED_MODE 0x01
    #endif

    /**
    *   Device normal mode bit settings.
    */
    #ifndef BME280_NORMAL_MODE
        #define BME280_NORMAL_MODE 0x03
    #endif

    /**
    *   Number of registers for temperature and pressure calibration data.
    */
    #ifndef BME280_TEMP_PRESS_CALIB_DATA_LEN
        #define BME280_TEMP_PRESS_CALIB_DATA_LEN 26
    #endif

    /**
    *   Number of registers for humidity calibration data.
    */
    #ifndef BME280_HUMIDITY_CALIB_DATA_LEN
        #define BME280_HUMIDITY_CALIB_DATA_LEN 7
    #endif

    /**
    *   Number of registers with pressure, temperature, and humidity data.
    */
    #ifndef BME280_P_T_H_DATA_LEN
        #define BME280_P_T_H_DATA_LEN 8
    #endif

    /**
    *   \brief Macro to concatenate bytes together.
    */
    #ifndef BME280_CONCAT_BYTES
        #define BME280_CONCAT_BYTES(msb, lsb)   (((uint16_t) msb << 8) | ((uint16_t) lsb))
    #endif
    

/* [] END OF FILE */
