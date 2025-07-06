library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity controller_ctf is
    Port ( clk : in STD_LOGIC;
           reset : in STD_LOGIC;
           zi : in STD_LOGIC;
           done : out STD_LOGIC;
           ldi : out STD_LOGIC;
           enflag : out STD_LOGIC;
           eni : out STD_LOGIC);
end controller_ctf;

architecture Behavioral of controller_ctf is

type state is (s_start, s_running, s_read, s_out, s_done);

signal p_state, n_state: state;

begin

    U_Mealy: process(clk, reset)
    begin
        if(reset = '1') then
            p_state <= s_start;
        elsif rising_edge(clk) then
            p_state <= n_state;
        end if;
    end process;
    
    Next_State_Output: process(zi, p_state)
    begin
        ldi <= '0';
        eni <= '0';
        enflag <= '0';
        
        case p_state is
            when s_start => 
                ldi <= '1';
                n_state <= s_running;
            when s_running =>
                enflag <= '1';
                eni <= '1';
                if zi = '1' then
                    n_state <= s_read;
                end if;
            when s_read =>
                ldi <= '1';
                n_state <= s_out;
            when s_out =>
                eni <= '1';
                if zi = '1' then
                    n_state <= s_done;
                end if;
            when s_done =>
                n_state <= s_done;
                done <= '1';
        end case;
    end process;
    
end Behavioral;