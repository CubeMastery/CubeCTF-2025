library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;


-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity RAM is
  generic 
	(
w: integer := 16; --word size
k: integer := 5 -- number of address bits
);
    Port ( clk : in STD_LOGIC;
           addr : in STD_LOGIC_VECTOR (k-1 downto 0);
           din : in STD_LOGIC_VECTOR (w-1 downto 0);
           dout : out STD_LOGIC_VECTOR (w-1 downto 0);
           we : in STD_LOGIC);
end RAM;

architecture behavioral of RAM is

type ram_type is array (0 to 2**k-1) of std_logic_vector(w-1 downto 0);
shared variable RAM: ram_type := (others =>(others=>'0'));

begin

RAM_process: process(clk)
begin
if rising_edge(clk) then
    dout <= RAM(to_integer(unsigned(addr))) AND "0000000011111111";
    if we = '1' then
        RAM(to_integer(unsigned(addr))) := din;
    end if;
end if;
end process;



end Behavioral;