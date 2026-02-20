from models.create_location_models.model_location_pg import FloorConfig, KeyLoc

def list_config_floor_other() -> list:
	configs_floor_other = [
		#ST CẤP HÀNG PM CHO XƯỞNG
		FloorConfig(
			location_name = ['PL' + loc for loc in 'DX,DC,DM,DJ,AU,DK,DQ,DF,AE,AK,PD,AM,DD,DW,DZ,DV,FE,DN,JA,FX,FC,FD,FR,CA,AT,AA'.split(',')],
			location_system_type = KeyLoc.LocSystemType.LSLPM,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.LSL_PM,
			location_category = KeyLoc.LocCategory.LSL,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.LSL,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#ST XƯỞNG RA HÀNG FG
		FloorConfig(
			location_name = ['ST' + loc for loc in 'DX,DC,DM,DJ,AU,DK,DQ,DF,AE,AK,PD,AM,DD,DW,DZ,DV,FE,DN,JA,FX,FC,FD,FR,CA,AT,AA'.split(',')],
			location_system_type = KeyLoc.LocSystemType.IN,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.LSL_IN,
			location_category = KeyLoc.LocCategory.LSL,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.LSL,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#ST LSL RM
		FloorConfig(
			location_name = ['HO10', 'HO03', 'PLMA', 'PLMD', 'PLMF', 'PLMK', 'HDLHEAT'],
			location_system_type = KeyLoc.LocSystemType.LSLRM,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.LSL_RM,
			location_category = KeyLoc.LocCategory.LSL,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.LSL,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#ST LINE RETURN
		FloorConfig(
			location_name = ['RTPD', 'RTMA', 'RTPA', 'RTMK'],
			location_system_type = KeyLoc.LocSystemType.LRT,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.LSL_LRT,
			location_category = KeyLoc.LocCategory.RETURN,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.LSL,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#LOCATION KHO SCHENKER
		FloorConfig(
			location_name = ['VN18'],
			location_system_type = KeyLoc.LocSystemType.EXWH,
			rack_system_type = KeyLoc.RackSystemType.OTHER,
			location_storage_type = KeyLoc.LocStorageType.OTHER,
			zone = KeyLoc.Zone.EXWH,
			location_category = KeyLoc.LocCategory.EXWH,
			location_product_category = KeyLoc.LocProducCategory.OTHER,
			name_warehouse = KeyLoc.NameWarehouse.EXWH,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#LOCATION HÀNG HỦY
		FloorConfig(
			location_name = ['STEAM1', 'STEAM2'],
			location_system_type = KeyLoc.LocSystemType.REJECT,
			rack_system_type = KeyLoc.RackSystemType.OTHER,
			location_storage_type = KeyLoc.LocStorageType.OTHER,
			zone = KeyLoc.Zone.STREAM_REJECT,
			location_category = KeyLoc.LocCategory.REJECT,
			location_product_category = KeyLoc.LocProducCategory.OTHER,
			name_warehouse = KeyLoc.NameWarehouse.STEAM,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#LOCATION CẮT MẪU
		FloorConfig(
			location_name = ['SAMP', 'MCSAMP'],
			location_system_type = KeyLoc.LocSystemType.SAMP,
			rack_system_type = KeyLoc.RackSystemType.OTHER,
			location_storage_type = KeyLoc.LocStorageType.OTHER,
			zone = KeyLoc.Zone.SAMP,
			location_category = KeyLoc.LocCategory.SAMP,
			location_product_category = KeyLoc.LocProducCategory.OTHER,
			name_warehouse = KeyLoc.NameWarehouse.WH2,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
	]

	return configs_floor_other