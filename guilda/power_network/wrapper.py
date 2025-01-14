from typing import Optional, Iterable

from guilda.power_network.types import SimulationOptions, SimulationScenario
from guilda.power_network.base import _PowerNetwork
from guilda.power_network.simulate import simulate

from guilda.utils.typing import FloatArray

class PowerNetwork(_PowerNetwork):
    
    
    def simulate(
        self, 
        scenario: SimulationScenario, 
        options: Optional[SimulationOptions] = None, 
        ):
        
        return simulate(self, scenario, options)
    
    def print_bus_state(self) -> None:
        for index in self.bus_index_map:
            b = self.a_bus_dict[index]
            print(f"Bus #{index} {type(b)}: ")
            print(f"  Vst: {b.V_equilibrium}")
            print(f"  Ist: {b.I_equilibrium}")
            print(f"  component.Vst: {b.component.V_equilibrium}")
            print(f"  component.Ist: {b.component.I_equilibrium}")
