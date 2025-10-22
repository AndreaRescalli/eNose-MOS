/**
 *
 * \file  BME280.h
 * \brief This header file contains all the functions declarations to
 *        interface with a BME280 sensor.
 *
 * The development of these funtions was taken by 
 * https://github.com/dado93/PSoC-Example-Projects/tree/master/BME280/01-BME280.cydsn
 * and modified ad-hoc for this project.
 *
 * \author Davide Marzorati, Damiano Rosario Tasso, Andrea Rescalli
 * \date   10/05/2023
 *
 */

#ifndef __BME280_H_
    #define __BME280_H_
    
    #include "project.h"
    #include "BME280_Macros.h"
    
    
    /******************************************/
    /*              Typedefs                  */
    /******************************************/
    /**
    *   Oversampling values.
    *
    *   All the possible values of Pressure oversampling.
    */
    typedef enum {
        BME280_NO_OVERSAMPLING,       ///< Oversampling skipped, output set to 0x8000
        BME280_OVERSAMPLING_1X,       ///< Oversampling x1
        BME280_OVERSAMPLING_2X,       ///< Oversampling x2
        BME280_OVERSAMPLING_4X,       ///< Oversampling x4
        BME280_OVERSAMPLING_8X,       ///< Oversampling x8
        BME280_OVERSAMPLING_16X       ///< Oversampling x16
    } BME280_Oversampling;
    
    /**
    *   Inactive duration (tStanbdy) in normal mode.
    *
    *   All the possible values of TStandby.
    */
    typedef enum {
        BME280_TSTANBDY_0_5_MS,  ///< TStandby: 0.5 ms
        BME280_TSTANBDY_62_5_MS, ///< TStandby: 62.5 ms
        BME280_TSTANBDY_125_MS,  ///< TStandby: 125 ms
        BME280_TSTANBDY_250_MS,  ///< TStandby: 250 ms
        BME280_TSTANBDY_500_MS,  ///< TStandby: 500 ms
        BME280_TSTANBDY_1000_MS, ///< TStandby: 1000 ms
        BME280_TSTANBDY_10_MS,   ///< TStandby: 10 ms
        BME280_TSTANBDY_20_MS,   ///< TStandby: 20 ms
    } BME280_TStandby;
    
    /**
    *   IIR Filter time constant
    *
    *   All the possible settings for the IIR Filter time constant.
    */
    typedef enum {
        BME280_FILTER_COEFF_OFF,  ///< Filter coeff skipped, output set to 0x8000
        BME280_FILTER_COEFF_2,    ///< Filter coeff x2
        BME280_FILTER_COEFF_4,    ///< Filter coeff x4
        BME280_FILTER_COEFF_8,    ///< Filter coeff x8
        BME280_FILTER_COEFF_16    ///< Filter coeff x16
    } BME280_Filter;
    
    /**
    *   Calibration coefficients
    *
    *   This struct holds the calibration coefficients of the sensor
    *   that can be read from registers #BME280_CALIB_TEMP_PRESS_REG_ADDR and
    *   #BME280_CALIB_HUM_REG_ADDR.
    */
    typedef struct {
        uint16_t dig_T1;    ///< Temperature calibration coefficient T1
        int16_t  dig_T2;    ///< Temperature calibration coefficient T2
        int16_t  dig_T3;    ///< Temperature calibration coefficient T3
        uint16_t dig_P1;    ///< Pressure calibration coefficient P1
        int16_t  dig_P2;    ///< Pressure calibration coefficient P2
        int16_t  dig_P3;    ///< Pressure calibration coefficient P3
        int16_t  dig_P4;    ///< Pressure calibration coefficient P4
        int16_t  dig_P5;    ///< Pressure calibration coefficient P5
        int16_t  dig_P6;    ///< Pressure calibration coefficient P6
        int16_t  dig_P7;    ///< Pressure calibration coefficient P7
        int16_t  dig_P8;    ///< Pressure calibration coefficient P8
        int16_t  dig_P9;    ///< Pressure calibration coefficient P9
        uint8_t  dig_H1;    ///< Humidity calibration coefficient H1
        int16_t  dig_H2;    ///< Humidity calibration coefficient H2
        uint8_t  dig_H3;    ///< Humidity calibration coefficient H3
        int16_t  dig_H4;    ///< Humidity calibration coefficient H4
        int16_t  dig_H5;    ///< Humidity calibration coefficient H5
        int8_t   dig_H6;    ///< Humidity calibration coefficient H6
        int32_t  t_fine;    ///< Fine temperature value
    } BME280_Calib_Data;
    
    /**
    *   Compensated data.
    */
    typedef struct {
        uint32_t pressure;      ///< Compensated pressure
        int32_t temperature;    ///< Compensated temperature
        uint32_t humidity;      ///< Compensated humidity
    } BME280_Data;
    
    /**
    *   Uncompensated data.
    */
    typedef struct {
        uint32_t pressure;      ///< Uncompensated pressure
        int32_t  temperature;   ///< Uncompensated temperature
        uint32_t humidity;      ///< Uncompensated humidity
    } BME280_Uncomp_Data;
    
    /**
    *   Sensor settings.
    *
    *   This structure allows to store the settings for sensor mode,
    *   oversampling (temperature, pressure, and humidity), filter,
    *   and stanby time.
    */
    typedef struct {
        uint8_t mode;        ///< Sensor mode setting
        uint8_t osr_p;       ///< Pressure oversampling setting
        uint8_t osr_t;       ///< Temperature oversampling setting   
        uint8_t osr_h;       ///< Humidity oversampling setting
        uint8_t filter;      ///< Filter setting
        uint8_t stanby_time; ///< Standby time setting
    } BME280_Settings;
    
    /**
    *   BME280 Device general structure.
    */
    typedef struct {
        uint8_t chip_id;                    ///< Chip id of the device
        BME280_Calib_Data calib_data;       ///< Structure for calibration data
        BME280_Data data;                   ///< Structure for sensor data
        BME280_Uncomp_Data uncomp_data;     ///< Structure for uncompensated data
        BME280_Settings settings;           ///< Structure for sensor settings
    } BME280;
    
    BME280 bme280; 
    
    /******************************************/
    /*          Function Prototypes           */
    /******************************************/
    /**
    *   Start the BME280 operation.
    *
    *   This function starts the BME280 sensor. This function checks if the
    *   device is connected by checking if a start condition is 
    *   acknowledged by the sensor. Then, it also reads the value of the
    *   #BME280_WHO_AM_I_REG_ADDR to check if the value is the expected one.
    *
    *   \param[in] bme280 : Pointer to device struct
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval #BME280_E_NULL_PTR -> Null pointer
    *   \retval #BME280_E_COMM_FAIL -> Error during I2C communication
    *   \retval #BME280_E_DEV_NOT_FOUND -> Device not found on I2C bus
    *   \retval #BME280_OK -> Success
    */
    BME280_ErrorCode BME280_Start(BME280* bme280);
    
    /**
    *   Reset the sensor.
    *
    *   This function reset the sensor by writing a 0xB6 value to the 
    *   reset register.  
    *
    *   \param[in] bme280 : pointer to device struct
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval #BME280_E_NULL_PTR -> Null pointer
    *   \retval #BME280_E_COMM_FAIL -> Error during I2C communication
    *   \retval #BME280_OK -> Success
    */
    BME280_ErrorCode BME280_Reset(BME280* bme280);
    
    /**
    *   Uncompensated data reading and compensation of them. 
    *
    *   This function reads the pressure, temperature, and humidity raw-values from the
    *   sensor, compensates them using the calibration data, and stores them.
    *
    *   The value of sensor_comp determines which data to compensate:
    *
    *    sensor_comp |   Macros
    *   -------------|-------------------
    *        1       | BME280_PRESS
    *        2       | BME280_TEMP
    *        4       | BME280_HUM
    *        7       | BME280_ALL
    *
    *   \param[in] bme280 : pointer to device structure
    *   \param[in] sensor_comp : flag to select which data to be compensated
    * --------------------------------------------------------------------------------
    *   \return Result of function execution
    *   \retval #BME280_E_NULL_PTR -> Null pointer
    *   \retval #BME280_E_COMM_FAIL -> Error during I2C communication
    *   \retval #BME280_OK -> Success
    */
    BME280_ErrorCode BME280_ReadData(BME280* bme280, uint8_t sensor_comp);
    
    /**
    *   Parse pressure, temperature, and humidity data.
    *
    *   This function parses pressure, temperature, and humidity data
    *   and stores them in the device structure.
    *
    *   \param[in] bme280 : Pointer to device struct
    *   \param[in] reg_data : Array with unparsed sensor data
    */
    void BME280_ParseSensorData(BME280* bme280, uint8_t* reg_data);
    
    /**
    *   Data compensation function
    *
    *   This function can be used to compensated the data of pressure and/or
    *   temperature and/or humidity according to the value of parameter sensor_comp.
    *
    *   \param[in] bme280 : pointer to device structure
    *   \param[in] sensor_comp : variable to select which values to compensate
    * --------------------------------------------------------------------------------
    *   \return Result of function execution
    *   \retval BME280_OK -> Success
    *   \retval BME280_ERROR -> Error
    */
    BME280_ErrorCode BME280_CompensateData(BME280* bme280, uint8_t sensor_comp);
    
    /**
    *   Get current sensor mode function.
    *
    *   This function retrieves the current sensor mode.
    *
    *   \param[in] bme280 : Pointer to device struct.
    * --------------------------------------------------------------------------------
    *   \return Result of function execution
    *   \retval BME280_OK -> Success
    *   \retval BME280_ERROR -> Error
    */
    BME280_ErrorCode BME280_GetSensorMode(BME280* bme280);
    
    /**
    *   Set humidity oversampling function.
    *
    *   This function sets the value of humidity oversampling by setting #BME280_CTRL_HUM_REG_ADDR 
    *   register. It also performs a write operation to the #BME280_CTRL_MEAS_REG_ADDR register
    *   because otherwise the changes won't become effective.
    *
    *   \param[in] hos : new value of #BME280_Oversampling
    *   \param[in] bme280 : pointer to device struct
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_SetHumidityOversampling(BME280* bme280, BME280_Oversampling hos);
    
    /**
    *   Set temperature oversampling function.
    *
    *   This function sets the value of temperature oversampling by setting the #BME280_CTRL_MEAS_REG_ADDR register. 
    *
    *   \param[in] bme280 : pointer to device struct
    *   \param[in] tos : new value of #BME280_Oversampling
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_SetTemperatureOversampling(BME280* bme280, BME280_Oversampling tos);
    
    /**
    *   Set pressure oversampling function.
    *
    *   This function sets the value of pressure oversampling by setting the #BME280_CTRL_MEAS_REG_ADDR register. 
    *
    *   \param[in] bme280 : pointer to device struct
    *   \param[in] pos : new value of #BME280_Oversampling
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_SetPressureOversampling(BME280* bme280, BME280_Oversampling pos);
    
    
    /**
    *   Read status register.
    *
    *   This function reads the #BME280_STATUS_REG_ADDR, that contains two bit[0][3]
    *   which indicate the status of the device.
    *
    *   \param[out] value : Value read from the status register
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_ReadStatusRegister(uint8_t* value);
    
    /**
    *   Set device in sleep mode.
    *
    *   This function sets the device in sleep mode by setting the #BME280_CTRL_MEAS_REG_ADDR.
    *
    *   \param[in] bme280 : pointer to device struct
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_SetSleepMode(BME280* bme280);
    
    /**
    *   Set device in forced mode.
    *
    *   This function sets the device in forced mode by setting the #BME280_CTRL_MEAS_REG_ADDR.
    *
    *   \param[in] bme280 : pointer to device struct
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_SetForcedMode(BME280* bme280);
    
    /**
    *   Set device in normal mode.
    *
    *   This function sets the device in normal mode by setting the #BME280_CTRL_MEAS_REG_ADDR.
    *
    *   \param[in] bme280 : pointer to device struct
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_SetNormalMode(BME280* bme280);
    
    /**
    *   Set TStandby value.
    *
    *   This function sets the new value for the inactive time in normal mode. 
    *
    *   \param[in] bme280 : pointer to device struct
    *   \param[in] t_standby : stanby time 
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_SetStandbyTime(BME280* bme280, BME280_TStandby t_standby);
    
    /**
    *   Set the value of IIR Filter.
    *
    *   This function sets the new value for the time constant of the 
    *   IIR filter. 
    *
    *   \param[in] bme280 : pointer to device struct
    *   \param[in] filter : value for IIR filter
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_SetIIRFilter(BME280* bme280, BME280_Filter filter);
    
    
    /******************************************/
    /*          Function Prototypes           */
    /******************************************/

    /**
    *   Set operation mode of the device.
    *
    *   This function sets the current mode of the device: 
    *   - sleep 
    *   - forced
    *   - normal
    *   by setting the #BME280_CTRL_MEAS_REG_ADDR register. 
    *
    *   \param[in] mode : new value of #BME280_Mode
    * --------------------------------------------------------------------------------
    *   \return Result of function execution.
    */
    BME280_ErrorCode BME280_SetMode(BME280* bme280, uint8_t mode);

    /**
    *   Raw temperature values compensation.
    *
    *   This function is used to compensate the raw temperature values and convert them
    *   in signed 32 bit integers.
    *
    *   \param[in] bme280 : pointer to device structure
    * --------------------------------------------------------------------------------
    *   \return Compensated temperature data.
    *   \retval Compensated temperature data as 32 bit signed integer.
    *
    */
    int32_t BME280_CompensateTemperature(BME280* bme280);

    /**
    *   Raw pressure values compensation.
    *
    *   This function is used to compensate the raw pressure values and convert them
    *   in unsigned 32 bit integers.
    *
    *   \param[in] bme280 : pointer to device structure
    * --------------------------------------------------------------------------------
    *   \return Compensated pressure data.
    *   \retval Compensated pressure data as 32 bit unsigned integer.
    *
    */
    int32_t BME280_CompensatePressure(BME280* bme280);
    
    /**
    *   Raw humidity values compensation.
    *
    *   This function is used to compensate the raw humidity values and convert them
    *   in unsigned 32 bit integers.
    *
    *   \param[in] bme280 : pointer to device structure
    * --------------------------------------------------------------------------------
    *   \return Compensated humidity data.
    *   \retval Compensated humidity data as 32 bit unsigned integer.
    *
    */
    uint32_t BME280_CompensateHumidity(BME280* bme280);


    /**
    *   Read Who Am I register value.
    *
    *   This function reads the value of the Who Am I register.
    *   If everything is set up correctly, you should read 0x60
    *
    *   \param[in] value : pointer to device value
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_ReadWhoAmI(uint8_t* value);

    /**
    *   Read device calibration data.
    *
    *   This function reads the calibration data from the sensor, parses
    *   them and stores them.
    *
    *   \param[in] bme280 Pointer to device struct
    * --------------------------------------------------------------------------------
    *   \return Result of function execution 
    *   \retval BME280_I2C_ERROR -> Error during I2C communication
    *   \retval BME280_ERROR -> Generic error
    *   \retval BME280_OK -> Success
    */
    BME280_ErrorCode BME280_ReadCalibrationData(BME280* bme280);

    /**
    *   Parse temperature and pressure calibration data.
    *
    *   This function parses temperature and pressure calibration data and
    *   stores them.
    *
    *   \param[in] bme280 Pointer to device struct
    *   \param[in] calib_data Array with unparsed calibration data
    */
    void BME280_ParseTempPressCalibData(BME280* bme280, uint8_t* calib_data);

    /**
    *   Parse humidity calibration data.
    *
    *   This function parses humidity calibration data and
    *   stores them.
    *
    *   \param[in] bme280 Pointer to device struct
    *   \param[in] calib_data Array with unparsed calibration data
    */
    void BME280_ParseHumidityCalibData(BME280* bme280, uint8_t* calib_data);

    /**
    *   Validate device structure for null conditions.
    *
    *   \param[in] bme280 : pointer to device structure
    * --------------------------------------------------------------------------------
    *   \return Result of null pointer check
    *   \retval BME280_OK -> Structure initialized
    *   \retval BME280_NULL_PTR ->
    */
    BME280_ErrorCode BME280_NullPtrCheck(const BME280* bme280);
    
    
    /*
    *   Fucntion which permits to read a register
    *   
    *   \param[in] register_address: register address
    *   \param[in] value: pointer to variable in which the register will be saved
    * --------------------------------------------------------------------------------
    *   \return BME280_ErrorCode
    */
    BME280_ErrorCode BME280_ReadRegister(uint8_t register_address, uint8_t* value);
    
    /*
    *   Function which initializes:
    *       - Humidity, temperature, pressure Oversampling at defalut value: BME280_OVERSAMPLING_1X.
    *       - Stand-by time at default value: 250 ms.
    *       - IIR filter coefficient at default value: 2.
    *
    *   \param[in] bm3280: pointer to bme280
    *   \param[in] array[]: pointer to the array to be sent
    * --------------------------------------------------------------------------------
    *   \return void
    */
    void BME280_DefaultInitRegisters(BME280* bm3280, uint8 array[]);
    
    /*
    *   Function which sets and saves in EEPROM
    *       - Humidity, temperature, pressure oversampling
    *       - Stand-by time
    *       - IIR filter coefficient
    *
    *   \param[in] bm3280: pointer to bme280
    *   \param[in] array[]: pointer to the array of parameters
    * --------------------------------------------------------------------------------
    *   \return void
    */
    void BME280_SetRegisters(BME280* bm3280, uint8 array[]);
    
    /*
    *   Function which sends the default settings 
    *
    *   \param[in] array[]: array to be sent
    * --------------------------------------------------------------------------------
    *   \return void
    */
    void BME280_SendDefaultSettings(uint8 array[]);
    
    /*
    *   Function which sends the new setting 
    *
    *   \param[in] array[]: array to be sent
    * --------------------------------------------------------------------------------
    *   \return void
    */
    void BME280_SendNewSettings(uint8 array[]);

#endif


/* [] END OF FILE */
