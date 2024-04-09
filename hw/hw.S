#    SPDX-FileCopyrightText: 2024 Gustavo Leite <gujoseleite@gmail.com>
#   
#    SPDX-License-Identifier: GPL-3.0-or-later
#
#    This file is part of SYSeg, available at https://gitlab.com/monaco/syseg.

#    Exercise 01

	# Boot, say hello, and halt
	# AT&T assembly, neater version wit loop

	.code16			                	# Set 16-bit mode
    .global _start                      # Define entrypoint

_start:                                 # Beginning of the program

	movb $0xe, %ah		                # Set BIOS to tty mode
    movw $0, %si                        # Initialize register to zero

loop:				
	movb $msg(%si), %al 	            # Offset each character in the message
	cmp $0, %al		                    # Comparing if char is not zero 
	je halt			                    # Jump to halt if char is zero
	int $0x10		                    # If not zero, call BIOS video interrupt
	add $0x1,%si 		                # Increment register by one to get the next character
	jmp loop		                    # Repeat until find a zero

halt:
	hlt			                        
	jmp halt		                    # Safeguard

msg:				        
	.string "Hello World"               # Define string
    .fill 510 - (. - _start), 1, 0      # Pad with zeros
	.word 0xaa55			            # Boot signature