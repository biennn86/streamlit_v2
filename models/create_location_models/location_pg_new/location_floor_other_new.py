from models.create_location_models.location_pg_new.model_location_pg_new import FloorConfig_New
from models.create_location_models.model_location_pg import KeyLoc

def list_config_floor_other_new() -> list:
	configs_floor_other_new = [
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
			is_active = 0,
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
	]
	
	return configs_floor_other_new