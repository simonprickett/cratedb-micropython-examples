from gfx_pack import SWITCH_E

import gfx
import cratedb
import time

import envvars

def refresh_crate_display():
    display = gfx.display
    
    gfx.clear_screen()
    gfx.set_backlight(0, 0, 0, 80)
    gfx.display_centered("UPDATING...", 25, 2)
    display.update()
    
    # Set up CrateDB.
    crate = cratedb.CrateDB(
        host=envvars.CRATEDB_HOST,
        user=envvars.CRATEDB_USER,
        password=envvars.CRATEDB_PASSWORD
    )
        
    response = crate.execute(
        """
            SELECT
              split_part(sensor_id, '.', 4) AS sensor_id,
              count(*) AS num_readings,
              trunc(avg(temp), 1) AS avg_temp,
              trunc(avg(humidity), 1) AS avg_humidity
            FROM
              sensor_readings
            WHERE
              timestamp >= (CURRENT_TIMESTAMP - INTERVAL '1' DAY)
            GROUP BY
              sensor_id
            ORDER BY 
              num_readings DESC
        """
    )
    
    rows = response["rows"]
    
    print(rows)
    
    gfx.clear_screen()
            
    v_pos = 10
    
    if len(rows) == 0:
        gfx.display_centered("No results.", 18, 2)
    else:    
        for row in rows:
            display.text(f"{row[0]}: {row[1]}", 5, v_pos, gfx.DISPLAY_WIDTH, 1)  
            v_pos += 10
       
    display.text("E: Exit", 95, 50, gfx.DISPLAY_WIDTH, 1)   
    display.update()
    
    
def run():
    refresh_crate_display()
    
    while True:
        time.sleep(0.01)
        
        if gfx.gp.switch_pressed(SWITCH_E):
            return
        
    