/*
 *    SPDX-FileCopyrightText: 2021 Monaco F. J. <monaco@usp.br>
 *    SPDX-FileCopyrightText: 2024 Gustavo Leite <gujoseleite@gmail.com>
 *   
 *    SPDX-License-Identifier: GPL-3.0-or-later
 *
 *  This file is a derivative work from SYSeg (https://gitlab.com/monaco/syseg)
 *  and contains modifications carried out by the following author(s):
 *  Gustavo Leite <gujoseleite@gmail.com>
 */

#include "bios.h"
#include "utils.h"

#define PROMPT "$ "		/* Prompt sign.      */
#define SIZE 20			/* Read buffer size. */

char buffer[SIZE];		/* Read buffer.      */

int main()
{
  clear();
  
  println  ("Boot Command 1.0");

  while (1) {
    print(PROMPT);		/* Show prompt.               */
    readln(buffer);		/* Read use input.            */

    if (buffer[0]) {
      if (!strcmp(buffer,"timedate")) {
	      timedate();
      } else {
	      println("Unkown command.");
      } 
	  }
  }
  
  return 0;

}

