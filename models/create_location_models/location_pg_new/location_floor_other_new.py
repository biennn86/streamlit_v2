from models.create_location_models.location_pg_new.model_location_pg_new import FloorConfig_New
from models.create_location_models.model_location_pg import KeyLoc

def list_config_floor_other_new() -> list:
	configs_floor_other_new = [
		# ST XƯỞNG TẠO HỆ THỐNG
		FloorConfig_New(
			location_name = [loc for loc in 'DX,DC,DM,DJ,AU,DK,DQ,DF,AE,AK,PD,AM,DD,DW,DZ,DV,FE,DN,JA,FX,FC,FD,FR,CA,AT,AA'.split(',')],
			location_system_type = KeyLoc.LocSystemType.IN,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.LSL_PM,
			location_category = KeyLoc.LocCategory.LSL,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.LSL,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		# ST CẤP HÀNG MỚI
		FloorConfig_New(
			location_name = ["ULIN" + loc for loc in 'DX,DC,DM,DJ,AU,DK,DQ,DF,AE,AK,PD,AM,DD,DW,DZ,DV,FE,DN,JA,FX,FC,FD,FR,CA,AT,AA'.split(',')],
			location_system_type = KeyLoc.LocSystemType.LSLPM,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.LSL_PM,
			location_category = KeyLoc.LocCategory.LSL,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.LSL,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#ST XƯỞNG RA HÀNG FG
		FloorConfig_New(
			location_name = ['LTA' + loc for loc in 'DX,DC,DM,DJ,AU,DK,DQ,DF,AE,AK,PD,AM,DD,DW,DZ,DV,FE,DN,JA,FX,FC,FD,FR,CA,AT,AA'.split(',')],
			location_system_type = KeyLoc.LocSystemType.IN,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.LSL_IN,
			location_category = KeyLoc.LocCategory.LSL,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.LSL,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.LOCK,
			note = None
			),
		#ST LINE RETURN
		FloorConfig_New(
			location_name = ['RTND1', 'RTND2', 'RTNDL'],
			location_system_type = KeyLoc.LocSystemType.LRT,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.LSL_LRT,
			location_category = KeyLoc.LocCategory.RETURN,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.LSL,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#ST KHO B
		FloorConfig_New(
			location_name = [st + "P" for st in ['ST17', 'ST18', 'ST19']] + ["PND" + st for st in ['ST17', 'ST18', 'ST19']],
			location_system_type = KeyLoc.LocSystemType.IN,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.WH1_IN,
			location_category = KeyLoc.LocCategory.RECEIVING,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.WH1,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#ST KHO B
		FloorConfig_New(
			location_name = [st + "P" for st in ['ST01', 'ST02', 'ST03', 'ST04']] + ["PND" + st for st in ['ST01', 'ST02', 'ST03', 'ST04']],
			location_system_type = KeyLoc.LocSystemType.IN,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.WH2_IN,
			location_category = KeyLoc.LocCategory.RECEIVING,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.WH2,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#ST WH2 OUT
		FloorConfig_New(
			location_name = ['ST' + str(i).zfill(2) + "P" for i in range(5, 17)] + ['PND' + 'ST' + str(i).zfill(2) for i in range(5, 17)] + ['ST-NDK' + str(i).zfill(2) for i in range(5, 17)],
			location_system_type = KeyLoc.LocSystemType.PICK,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.WH2_FLOOR,
			location_category = KeyLoc.LocCategory.PICKING,
			location_product_category = KeyLoc.LocProducCategory.OTHER,
			name_warehouse = KeyLoc.NameWarehouse.WH2,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#VỊ TRÍ ĐƯỜNG LUỒNG WH2 MỚI HỆ THỐNG PRIME
		FloorConfig_New(
			location_name = ['F2WFA', 'F2WFB', 'F2WFC', 'F2WFD', 'F2WFE', 'F2WFF', 'F2WFG', 'F2WFH', 'F2WFI', 'F2WFK', 'F2WFL', 'F2WFM'],
			location_system_type = KeyLoc.LocSystemType.WW,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.WH2_WW,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.WH2,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.LOCK,
			note = None
			),
		#VỊ TRÍ ĐƯỜNG LUỒNG WH3 MỚI HỆ THỐNG PRIME
		FloorConfig_New(
			location_name = ['PROBLEM', 'F2WG1G2', 'F2WG3G4', 'F2WG5G6', 'F2WG7G8'],
			location_system_type = KeyLoc.LocSystemType.WW,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.WH3_WW,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.WH3,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.LOCK,
			note = None
			),
		#ST CẤP HÀNG MỚI PRIME
		FloorConfig_New(
			location_name = ["PL" + loc + "C" for loc in 'DX,DC,DM,DJ,AU,DK,DQ,DF,AE,AK,PD,AM,DD,DW,DZ,DV,FE,DN,JA,FX,FC,FD,FR,CA,AT,AA'.split(',')],
			location_system_type = KeyLoc.LocSystemType.LSLPM,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.LSL_PM,
			location_category = KeyLoc.LocCategory.LSL,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.LSL,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#LOCATION TRẢ HÀNG LẺ KHI XUẤT HÀNG MỚI PRIME
		FloorConfig_New(
			location_name = ['STRETURN'],
			location_system_type = KeyLoc.LocSystemType.RETURN,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.WH2_RETURN,
			location_category = KeyLoc.LocCategory.RETURN,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.WH2,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#ST LSL RM
		FloorConfig_New(
			location_name = ['HO10C', 'HO03C', 'PLMAC', 'PLMDC', 'PLMFC', 'PLMKC'],
			location_system_type = KeyLoc.LocSystemType.LSLRM,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.LSL_RM,
			location_category = KeyLoc.LocCategory.LSL,
			location_product_category = KeyLoc.LocProducCategory.FG_RPM,
			name_warehouse = KeyLoc.NameWarehouse.LSL,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 1,
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
	]
	
	return configs_floor_other_new