library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all; 

entity datapath_ctf is
    Port ( clk : in STD_LOGIC;
           reset : in STD_LOGIC;
           eni : in STD_LOGIC;
           enflag : in STD_LOGIC;
           ldi : in STD_LOGIC;
           din : in STD_LOGIC_VECTOR(15 downto 0);
           dout : out STD_LOGIC_VECTOR(15 downto 0);
           zi : out STD_LOGIC);
end datapath_ctf;

architecture Mixed of datapath_ctf is

signal i : integer range 0 to 32;
signal flag_en : std_logic;
signal flag_in, flag_out : std_logic_vector(15 downto 0);
signal flag_addr : std_logic_vector(4 downto 0);
signal index : integer range 0 to 31 := 0;


begin
    zi <= '1' when i = 31 else '0';    
    
    index <= (i * 5) mod 32;
    
    iupcount: PROCESS(clk, reset)
    BEGIN
        if reset = '1' then
            i <= 0;
        elsif rising_edge(clk) then
            if ldi = '1' then
                i <= 0;
            elsif eni = '1' then                                    
                i <= i + 1;                 
            end if;

    
        end if;
    end process;
    
--    readout : PROCESS(clk, reset)
--    BEGIN
--        if reset = '1' then
--            index <= 0;
--        elsif rising_edge(clk) then               
--            index <= (i * 5) mod 32;
--        end if;
--    end process;
  
    
    flag_process: PROCESS(clk, reset)
        BEGIN
            if reset = '1' then
                flag_en <= '0';
            elsif rising_edge(clk) then
                if enflag = '1' then
                    flag_addr <= std_logic_vector(to_unsigned(i, flag_addr'length));
                    flag_en <= '1';
                    flag_in <= din;
                else
                    flag_en <= '0';
                    flag_addr <= std_logic_vector(to_unsigned(index, flag_addr'length));
                end if;
                dout <= std_logic_vector(to_unsigned(to_integer(unsigned(flag_out)) - 32, dout'length));
            end if;
        end process;   
                
        
   flag: entity work.RAM 
    generic map(w=>16, 
       k=>5)
    port map(
      din => flag_in,
      dout => flag_out, 
      addr => flag_addr,
      we => flag_en,
      clk => clk
    );
    
    


end Mixed;
