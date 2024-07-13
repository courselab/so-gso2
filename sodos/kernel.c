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

/* This source file implements the kernel entry function 'kmain' called
   by the bootloader, and the command-line interpreter. Other kernel functions
   were implemented separately in another source file for legibility. */

#include "bios1.h"		/* For kwrite() etc.            */
#include "bios2.h"		/* For kread() etc.             */
#include "kernel.h"		/* Essential kernel functions.  */
#include "kaux.h"		/* Auxiliary kernel functions.  */
#include <stddef.h>

#define DIR_ENTRY_LEN 32 	                /* Max file name length in bytes.           */
#define FS_SIGLEN 4                       /* Signature length.                        */
#define HEADER_START 0x7c00               
#define SECTOR_SIZE 512

/* Kernel's entry function. */

void kmain(void)
{
  int i, j;
  
  register_syscall_handler();	/* Register syscall handler at int 0x21.*/

  splash();			/* Uncessary spash screen.              */

  shell();			/* Invoke the command-line interpreter. */
  
  halt();			/* On exit, halt.                       */
  
}

/* Tiny Shell (command-line interpreter). */

char buffer[BUFF_SIZE];
int go_on = 1;

void shell()
{
  int i;
  clear();
  kwrite ("Welcome to SODOS 1.0\n");

  while (go_on)
    {

      /* Read the user input. 
	 Commands are single-word ASCII tokens with no blanks. */
      do
	{
	  kwrite(PROMPT);
	  kread (buffer);
	}
      while (!buffer[0]);

      /* Check for matching built-in commands */
      
      i=0;
      while (cmds[i].funct)
	{
	  if (!strcmp(buffer, cmds[i].name))
	    {
	      cmds[i].funct();
	      break;
	    }
	  i++;
	}

      /* If the user input does not match any built-in command name, just
	 ignore and read the next command. If we were to execute external
	 programs, on the other hand, this is where we would search for a 
	 corresponding file with a matching name in the storage device, 
	 load it and transfer it the execution. Left as exercise. */
      
    if (!cmds[i].funct)
      f_exec(buffer);
    }
}

/* Array with built-in command names and respective function pointers. 
   Function prototypes are in kernel.h. */

struct cmd_t cmds[] =
  {
    {"help",    f_help},     /* Print a help message.       */
    {"quit",    f_quit},     /* Exit TyDOS.                 */
    {"list",    f_list},     /* List disk files. */
    {0, 0}
  };


/* Build-in shell command: help. */

void f_help()
{
  kwrite ("...oh, Do you need some help?!\n\n");
  kwrite ("  We can try also some commands:\n");
  kwrite ("    list   (to list all files in disk\n");
  kwrite ("    quit   (to exit SODOS)\n");
}

void f_quit()
{
  kwrite ("Program halted. ByeSODOS.");
  go_on = 0;
}

/* Header struct */

struct fs_header_t
{
  unsigned char  signature[FS_SIGLEN];    /* The file system signature.              */
  unsigned short total_number_of_sectors; /* Number of 512-byte disk blocks.         */
  unsigned short number_of_boot_sectors;  /* Sectors reserved for boot code.         */
  unsigned short number_of_file_entries;  /* Maximum number of files in the disk.    */
  unsigned short max_file_size;		        /* Maximum size of a file in blocks.       */
  unsigned int unused_space;              /* Remaining space less than max_file_size.*/
} __attribute__((packed));                /* Disable alignment to preserve offsets.  */

/* List files function */

void f_list() {

    struct fs_header_t *header = (struct fs_header_t *) HEADER_START;

    // Calculate the starting sector of the directory list
    unsigned int start_sector = header->number_of_boot_sectors;
    
    // Calculate the number of sectors to read 
    unsigned int sectors_to_read = header->number_of_file_entries * 32 / SECTOR_SIZE;

    // Allocate buffer in RAM to load the directory list
    void *section_memory_to_load = (void*)(start_sector * SECTOR_SIZE);

    // Read the specified number of sectors from the disk into the allocated RAM buffer
    read_disk(start_sector, sectors_to_read, section_memory_to_load);

    for (size_t i = 0; i < header->number_of_file_entries; i++) {
        // Calculate the address of the current filename
        const char *filename = section_memory_to_load + (i * DIR_ENTRY_LEN);
        
        if (filename[0] == '\0') {
            continue;
        }

        kwrite(filename);
        kwrite("\n"); 
    }
}


/* Built-in shell command: example.

   Execute an example user program which invokes a syscall.

   The example program (built from the source 'prog.c') is statically linked
   to the kernel by the linker script (tydos.ld). In order to extend the
   example, and load and external C program, edit 'f_exec' and 'prog.c' choosing
   a different name for the entry function, such that it does not conflict with
   the 'main' function of the external program.  Even better: remove 'f_exec'
   entirely, and suppress the 'example_program' section from the tydos.ld, and
   edit the Makefile not to include 'prog.o' and 'libtydos.o' from 'tydos.bin'.

  */

void f_exec(const char* prog_name)
{
  struct fs_header_t *header = (struct fs_header_t *) HEADER_START;

  // Calculate the starting sector of the directory list
   unsigned int start_sector = header->number_of_boot_sectors;
    
  // Calculate the number of sectors to read 
  unsigned int sectors_to_read = header->number_of_file_entries * 32 / SECTOR_SIZE;

  // Allocate buffer in RAM to load the directory list
  void *section_memory_to_load = (void*)(start_sector * SECTOR_SIZE);

  // Read the specified number of sectors from the disk into the allocated RAM buffer
  read_disk(start_sector, sectors_to_read, section_memory_to_load);

  unsigned int prog_address = -1;
  for (size_t i = 0; i < header->number_of_file_entries; i++) {
    char *filename = section_memory_to_load + (i * DIR_ENTRY_LEN);
    if (strcmp(filename, prog_name) == 0) {
      prog_address = start_sector + sectors_to_read + (i * DIR_ENTRY_LEN);
      break;
    }
  }

  if (prog_address == -1) {
    kwrite("Program not found on the disk.\n");
    return;
  }

  unsigned int memory_offset = header->number_of_file_entries * 32 - (sectors_to_read - 1) * SECTOR_SIZE;
  void *section_memory_to_prog = (void *)(0xfe00) - memory_offset;
  
  read_disk(prog_address, header->max_file_size, section_memory_to_prog);

  exec();
}

extern int main();
