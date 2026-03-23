.syntax unified
.cpu cortex-a9
.fpu vfpv3
.global _start

.text
_start:
    ldr r10, =eval_stack
    mov r11, #0

line_0:
    ldr r4, =const_0
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_1
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vadd.f64 d0, d1, d0
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_0
    vstr d0, [r4]
    mov r11, #0

line_1:
    ldr r4, =const_2
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_3
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vsub.f64 d0, d1, d0
    bl push_d0
    ldr r4, =const_4
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_5
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vadd.f64 d0, d1, d0
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vmul.f64 d0, d1, d0
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_1
    vstr d0, [r4]
    mov r11, #0

line_2:
    ldr r4, =const_6
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_7
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vdiv.f64 d0, d1, d0
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_2
    vstr d0, [r4]
    mov r11, #0

line_3:
    ldr r4, =const_6
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_7
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    bl op_int_div
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_3
    vstr d0, [r4]
    mov r11, #0

line_4:
    ldr r4, =const_6
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_7
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    bl op_int_mod
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_4
    vstr d0, [r4]
    mov r11, #0

line_5:
    ldr r4, =const_4
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_8
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    bl op_pow_int
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_5
    vstr d0, [r4]
    mov r11, #0

line_6:
    ldr r4, =const_9
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    ldr r4, =mem_VAR
    vstr d0, [r4]
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_6
    vstr d0, [r4]
    mov r11, #0

line_7:
    ldr r4, =mem_VAR
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_7
    vstr d0, [r4]
    mov r11, #0

line_8:
    ldr r4, =mem_VAR
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_10
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vadd.f64 d0, d1, d0
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_8
    vstr d0, [r4]
    mov r11, #0

line_9:
    ldr r4, =const_11
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_5
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vadd.f64 d0, d1, d0
    bl push_d0
    ldr r4, =result_8
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vdiv.f64 d0, d1, d0
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_9
    vstr d0, [r4]
    mov r11, #0

line_10:
    ldr r4, =const_5
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_3
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vadd.f64 d0, d1, d0
    bl push_d0
    ldr r4, =const_4
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_8
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vadd.f64 d0, d1, d0
    bl push_d0
    ldr r4, =const_3
    vldr d0, [r4]
    bl push_d0
    ldr r4, =const_5
    vldr d0, [r4]
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vsub.f64 d0, d1, d0
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vmul.f64 d0, d1, d0
    bl push_d0
    bl pop_to_d0
    bl pop_to_d1
    vsub.f64 d0, d1, d0
    bl push_d0
    bl pop_to_d0
    ldr r4, =result_10
    vstr d0, [r4]
    mov r11, #0

end_program:
    b end_program

push_d0:
    vstr d0, [r10, r11]
    add r11, r11, #8
    bx lr

pop_to_d0:
    cmp r11, #0
    beq runtime_error
    sub r11, r11, #8
    vldr d0, [r10, r11]
    bx lr

pop_to_d1:
    cmp r11, #0
    beq runtime_error
    sub r11, r11, #8
    vldr d1, [r10, r11]
    bx lr

op_int_div:
    vcvt.s32.f64 s2, d1
    vcvt.s32.f64 s3, d0
    vmov r0, s2
    vmov r1, s3
    bl int_divide_signed
    vmov s0, r0
    vcvt.f64.s32 d0, s0
    bx lr

op_int_mod:
    vcvt.s32.f64 s2, d1
    vcvt.s32.f64 s3, d0
    vmov r0, s2
    vmov r1, s3
    bl int_mod_signed
    vmov s0, r0
    vcvt.f64.s32 d0, s0
    bx lr

op_pow_int:
    vcvt.s32.f64 s1, d0
    vmov r0, s1
    cmp r0, #0
    blt runtime_error
    ldr r4, =const_one
    vldr d0, [r4]
    vmov.f64 d2, d1
pow_loop:
    cmp r0, #0
    beq pow_done
    vmul.f64 d0, d0, d2
    sub r0, r0, #1
    b pow_loop
pow_done:
    bx lr

int_divide_signed:
    cmp r1, #0
    beq runtime_error
    mov r2, #0
    cmp r0, #0
    bge div_a_ok
    rsb r0, r0, #0
    eor r2, r2, #1
div_a_ok:
    cmp r1, #0
    bge div_b_ok
    rsb r1, r1, #0
    eor r2, r2, #1
div_b_ok:
    mov r3, #0
div_loop:
    cmp r0, r1
    blt div_done
    sub r0, r0, r1
    add r3, r3, #1
    b div_loop
div_done:
    mov r0, r3
    cmp r2, #0
    beq div_exit
    rsb r0, r0, #0
div_exit:
    bx lr

int_mod_signed:
    cmp r1, #0
    beq runtime_error
    mov r2, #0
    cmp r0, #0
    bge mod_a_ok
    rsb r0, r0, #0
    mov r2, #1
mod_a_ok:
    cmp r1, #0
    bge mod_b_ok
    rsb r1, r1, #0
mod_b_ok:
mod_loop:
    cmp r0, r1
    blt mod_done
    sub r0, r0, r1
    b mod_loop
mod_done:
    cmp r2, #0
    beq mod_exit
    rsb r0, r0, #0
mod_exit:
    bx lr

runtime_error:
    b runtime_error

.data
eval_stack: .space 8192
const_one: .double 1.0
const_0: .double 8.25
const_1: .double 1.75
const_2: .double 7
const_3: .double 2
const_4: .double 3
const_5: .double 1
const_6: .double 20
const_7: .double 6
const_8: .double 4
const_9: .double 2.5
const_10: .double 1.5
const_11: .double 5
mem_VAR: .double 0.0
result_0: .double 0.0
result_1: .double 0.0
result_2: .double 0.0
result_3: .double 0.0
result_4: .double 0.0
result_5: .double 0.0
result_6: .double 0.0
result_7: .double 0.0
result_8: .double 0.0
result_9: .double 0.0
result_10: .double 0.0
