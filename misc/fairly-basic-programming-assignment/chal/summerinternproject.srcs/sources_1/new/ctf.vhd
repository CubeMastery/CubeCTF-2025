library IEEE;
use IEEE.STD_LOGIC_1164.ALL;


entity ctf is
    Port ( clk : in STD_LOGIC;
           reset : in STD_LOGIC;
           din : in STD_LOGIC_VECTOR(15 downto 0);
           dout : out STD_LOGIC_VECTOR(15 downto 0);
           done : out STD_LOGIC
           );
end ctf;

architecture Structure of ctf is

signal zi : STD_LOGIC;
signal eni : STD_LOGIC;
signal ldi : STD_LOGIC;
signal enflag : STD_LOGIC;


begin

    controller_ctf : entity work.controller_ctf(Behavioral)
    PORT MAP(clk => clk,
            reset => reset,
            zi => zi,
            eni => eni,
            enflag => enflag,
            done => done,
            ldi => ldi);
     datapath_ctf : entity work.datapath_ctf(Mixed)
     PORT MAP(clk => clk,
              reset => reset,
              din => din,
              dout => dout,
              zi => zi,
              eni => eni,
              enflag => enflag,
              ldi => ldi);


end Structure;
