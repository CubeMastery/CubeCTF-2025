LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;
use ieee.std_logic_textio.all;
library std;
use std.textio.all;

entity ctf_testbench is
--  Port ( );
end ctf_testbench;

architecture Behavioral of ctf_testbench is

   --Inputs
    signal clk : std_logic := '0';
    signal reset : std_logic := '0';
    signal din : std_logic_vector(15 downto 0) := (others => '0');
    signal dout : std_logic_vector(15 downto 0) := (others => '0'); 
    
    constant clk_period : time := 10 ns;
    
    type input_array is array (0 to 31) of std_logic_vector(15 downto 0);
constant test_data : input_array := (
    x"1275", x"D453", x"9E77", x"AA9B",  --3
    x"0167", x"8073", x"8972", x"C053", --7
    x"D166", x"0850", x"1C63", x"A466", --11
    x"C973", x"0E75", x"1F50", x"2067", --15
    x"E353", x"B275", x"7F6E", x"FE64", --19
    x"A963", x"DA63", x"016D", x"9A7F", --23
    x"C07F", x"1474", x"D474", x"B99D", --27
    x"E370", x"C361", x"A366", x"D07F" --31
);


begin

   dut: ENTITY work.ctf(Structure)
   port map (
          clk   => clk,
          reset => reset,
          din => din,
          dout => dout);
          
   clk <= not clk after clk_period/2;
   
   stim_proc: process

   begin
        reset <= '1';
        wait for clk_period;
        reset <= '0';
        wait for clk_period;
        
        for i in 0 to 31 loop
            din <= test_data(i);
            wait for clk_period;
        end loop;
        
        
        wait;
        
   end process;


end Behavioral;
