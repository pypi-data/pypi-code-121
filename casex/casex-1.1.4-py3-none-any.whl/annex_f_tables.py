import numpy as np
from casex import enums, FrictionCoefficients, CriticalAreaModels, AircraftSpecs, AnnexFParms

class AnnexFTables:
    
    @staticmethod
    def iGRC_tables(show_with_obstacles = True,
                    show_ballistic = False,
                    show_convervative_reduction = False,
                    show_CFIT_angle = True,
                    show_additional_pop_density = True):
        """Compute the iGRC tables Annex F :cite:`a-JARUS_AnnexF`.
        
        Forklaring her
        
        Parameters
        ----------
        xxx : bool
            xxx
            
        Returns
        -------
        console_output : list of strings
            The output to show.
        """
        #show_with_obstacles = True
        #show_ballistic = False
        #show_convervative_reduction = False
        #show_CFIT_angle = True
        #show_additional_pop_density = True
        
        # Data on person size.
        person_width = 0.3
        person_height = 1.8
        
        # Set impact angle.
        impact_angle = 9 if show_CFIT_angle else 35
        
        # Instantiate necessary classes.
        CA = CriticalAreaModels(person_width, person_height)
        AFP = AnnexFParms(impact_angle)
        
        # Instantiate and add data to AircraftSpecs class.
        # Values are not relevant here, since they will be changed below.
        aircraft = AircraftSpecs(enums.AircraftType.GENERIC, 1, 1, 1)
        
        # Friction coefficient from Annex F.
        aircraft.set_friction_coefficient(AFP.friction_coefficient)
        
        # Set parameters for fuel
        aircraft.set_fuel_type(enums.FuelType.GASOLINE)
        aircraft.set_fuel_quantity(0)
        
        # Set list of population density bands in the table.
        pop_density = np.array([0.1, 10, 100, 1500, 15000, 100000])
        
        if show_additional_pop_density:
            pop_density = np.append(pop_density, [30, 300, 2000, 2500, 3000, 10000, 20000, 50000])
        
        pop_density = np.sort(pop_density)
        
        # Initialize variables.,
        iGRC_table = np.zeros((len(pop_density), 5))
        impact_angles = np.zeros((5))
        p = np.zeros((5, 5))
        
        # Loop over columns in the iGRC table.
        for j in range(0, 5):
            
            # Set mass according to Annex F.
            aircraft.set_mass(AFP.CA_parms[j].mass)
        
            # First, set width and speed to nominal values.
            aircraft.set_width(AFP.CA_parms[j].wingspan)
            
            if show_ballistic:
                impact_speed = AFP.CA_parms[j].ballistic_impact_velocity
                impact_angle = AFP.CA_parms[j].ballistic_impact_angle
            else:
                impact_speed = AFP.CA_parms[j].glide_speed if show_CFIT_angle else AFP.CA_parms[j].cruise_speed
        
            # Get CoR using the aircraft class.
            if j > 1:
                aircraft.set_coefficient_of_restitution(aircraft.COR_from_impact_angle(impact_angle))
            else:
                aircraft.set_coefficient_of_restitution(0.9)
        
            # Compute the CA.
            p[j] = CA.critical_area(enums.CriticalAreaModel.JARUS, aircraft, impact_speed, impact_angle, 0, -1)
            
            # Store the impact angle (only relevant for ballistic).
            impact_angles[j] = impact_angle
        
        # Compute the iGRC values.
        for i in range(len(pop_density)):
            for j in range(0, 5):
                iGRC_table[i][j] = AFP.iGRC(pop_density[i],
                                            p[j][0],
                                            use_obstacle_reduction = show_with_obstacles,
                                            use_convervative_reduction = show_convervative_reduction)[1]
        console_output = []
        
        s = "Final iGRC"
        s = s + " (ballistic)" if show_ballistic else s + " ({:d} deg)".format(impact_angle)
        console_output.append(s)
            
        console_output.append("                          1 m       3 m       8 m      20 m      40 m")
        console_output.append("--------------------+-------------------------------------------------")
        
        for i in range(len(pop_density)):
            
            if (pop_density[i] > 1):
                s = "{:7.0f} [ppl/km^2]  | ".format(pop_density[i])
            else:
                s = "Controlled (< 0.1)  | "
         
            for j in range(0, 5):
                s = s + "{:7.1f}   ".format(iGRC_table[i][j])
            
            console_output.append(s)
            
        console_output.append("--------------------+-------------------------------------------------")
        
        s = "     CA size [m^2]  |"
        for j in range(0, 5):
            s = s + "{:8.0f}  ".format(p[j][0])
        console_output.append(s)
        
        s = "Slide distance [m]  |"
        for j in range(0, 5):
            s = s + "{:8.0f}  ".format(p[j][2] / AFP.CA_parms[j].wingspan)
        console_output.append(s)
        
        if show_ballistic:
            s = "Impact angle [deg]  |"
            for j in range(0, 5):
                s = s + "{:8.0f}  ".format(impact_angles[j])
            console_output.append(s)
            
            s = "Altitude [m]        |    "
            for k in range(5):
                s = s + "{:4.0f}      ".format(AFP.CA_parms[k].ballistic_descent_altitude)
            console_output.append(s)
            
            s = "Impact angle [deg]  |    "
            for k in range(5):
                s = s + "{:4.1f}      ".format(AFP.CA_parms[k].ballistic_impact_angle)
            console_output.append(s)
        
            s = "Impact vel [m/s]    |   "    
            for k in range(5):
                s = s + "{:5.1f}     ".format(AFP.CA_parms[k].ballistic_impact_velocity)
            console_output.append(s)
        
            s = "Drag area [m^2]     |    "
            for k in range(5):
                s = s + "{:4.1f}      ".format(AFP.CA_parms[k].ballistic_frontal_area)
            console_output.append(s)
                
        console_output.append("--------------------+-------------------------------------------------")
    
        return console_output   