# Fairly Basic Programming Assignment

**tl;dr**

1. Observe that the input width is 16 bits, but the upper 8 bits are masked off. Discard the top 8 bits of every input value.
2. Reverse the VHDL to understand how it shuffles the input.
3. Unshuffle the input.
4. Subtract 0x20 from every output byte.

## Description

>We wanted the intern to learn how to code... but we're not quite sure what he did here. Can you make any sense of what it does? (flag format: USCGCTF{flag})

## Solution

`ctf_testbench.vhd` defines an input array of 32 16-bit values.

```
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
```

Then further down, it assigns `din` to each value in the input array once per `clk_period` in order.

```
        for i in 0 to 31 loop
            din <= test_data(i);
            wait for clk_period;
        end loop;
```

Concurrently, once every rising edge of the clock, the ram process reads a value from din to a `RAM` when `we` is 1 (more on this state later).

```
RAM_process: process(clk)
begin
if rising_edge(clk) then
    dout <= RAM(to_integer(unsigned(addr))) AND "0000000011111111";
    if we = '1' then
        RAM(to_integer(unsigned(addr))) := din;
    end if;
end if;
end process;
```

The controller operates the state machine:

```
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
```

Notably the states, progress from `s_start` -> `s_running` -> `s_read` -> `s_out` -> `s_done`. When the state is `s_running`, `enflag` is 1.

The datapath defines the operations that take place during each state.

```
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
```

If `enflag` is 1 it sets `we` which enables the `ram` process to read from `din` to the `RAM`. In other words, during the `s_running` state, the input array from `testbench` will be read in from `din`.

After the `s_running` state iterates 32 times (reading 32 chars), it sets `zi` to 1. This triggers the state change to `s_read`. `s_read` sets `ldi`, triggering `i` to revert to 0 and continues on to `s_out`. In `s_out`, we will iterate 32 times again, this time setting the flag addr to `index`, which is `(i*5) % 32`:

```
                else
                    flag_en <= '0';
                    flag_addr <= std_logic_vector(to_unsigned(index, flag_addr'length));
                end if;
                dout <= std_logic_vector(to_unsigned(to_integer(unsigned(flag_out)) - 32, dout'length));
```

During the `s_out` state, the `ram` process will output the lower 8 bits based on `flag_addr` (which is `index`) to `dout`. The `datapath` will subtract 32 from each output byte. We assume these are the flag bytes. Indeed, once we understand all the pieces of the puzzle, the unscramble operation is incredibly simple.

```python
b = [
    "75", "53", "77", "9B",
    "67", "73", "72", "53",
    "66", "50", "63", "66",
    "73", "75", "50", "67",
    "53", "75", "6E", "64",
    "63", "63", "6D", "7F",
    "7F", "74", "74", "9D",
    "70", "61", "66", "7F"
]

for i in range(len(b)):
    cur_byte = int(b[(5*i)%32], 16)
    print(chr(cur_byte - 32 ), end='')
```
