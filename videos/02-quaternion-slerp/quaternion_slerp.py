from manim import *
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from manim_style import *


def orientation_arrow(center, angle, radius=1.55, color=X_RED):
    return clean_arrow(center, center + radius*np.array([np.cos(angle), np.sin(angle), 0]), color, 3.2, 0.15)


class QuaternionSlerpExplainer(Scene):
    def construct(self):
        self.half_angle()
        self.unit_norm()
        self.double_cover()
        self.composition()
        self.slerp()
        self.recap()

    def half_angle(self):
        add_base(self)
        h = header(1, "AXIS–ANGLE → QUATERNION", "物理角度 α，为什么在四元数里变成 α/2？")
        lc, rc = LEFT*3.2+DOWN*0.2, RIGHT*3.2+DOWN*0.2
        physical_circle = Circle(1.85, color=LINE, stroke_width=1.5).move_to(lc)
        quat_circle = Circle(1.85, color=LINE, stroke_width=1.5).move_to(rc)
        alpha = ValueTracker(0)
        p_arrow = always_redraw(lambda: orientation_arrow(lc, alpha.get_value(), 1.75, X_RED))
        q_arrow = always_redraw(lambda: orientation_arrow(rc, alpha.get_value()/2, 1.75, VIOLET))
        p_arc = always_redraw(lambda: Arc(0.55, 0, max(alpha.get_value(),0.01), arc_center=lc, color=X_RED, stroke_width=2.0))
        q_arc = always_redraw(lambda: Arc(0.55, 0, max(alpha.get_value()/2,0.01), arc_center=rc, color=VIOLET, stroke_width=2.0))
        p_tag = always_redraw(lambda: code_text(f"α = {int(round(alpha.get_value()/DEGREES))}°", 20, X_RED, MEDIUM).next_to(lc, DOWN, buff=2.05))
        q_tag = always_redraw(lambda: code_text(f"α/2 = {int(round(alpha.get_value()/DEGREES/2))}°", 20, VIOLET, MEDIUM).next_to(rc, DOWN, buff=2.05))
        left_title = label_chip("物理旋转", X_RED).next_to(lc, UP, buff=2.0)
        right_title = label_chip("单位四元数圆截面", VIOLET).next_to(rc, UP, buff=2.0)
        formula = formula_bar("q = ( cos(α/2),  u·sin(α/2) )", CYAN, size=22).to_edge(DOWN, buff=0.22)

        self.play(FadeIn(h), Create(physical_circle), Create(quat_circle), FadeIn(left_title,right_title), run_time=0.9)
        self.add(p_arrow,q_arrow,p_arc,q_arc,p_tag,q_tag)
        self.play(FadeIn(formula), run_time=0.5)
        self.play(alpha.animate.set_value(120*DEGREES), run_time=3.0, rate_func=smooth)
        self.wait(1.4)
        fade_all(self)

    def unit_norm(self):
        add_base(self)
        h = header(2, "UNIT QUATERNION", "合法旋转位于单位球面，长度不能漂移")
        c = LEFT*2.7+DOWN*0.15
        circle = Circle(2.0, color=VIOLET, stroke_width=1.7).move_to(c).set_fill(opacity=0).set_stroke(opacity=0.65)
        bad_point = c + np.array([2.75,1.0,0])
        good_point = c + 2.0*np.array([np.cos(20*DEGREES),np.sin(20*DEGREES),0])
        bad = Dot(bad_point, radius=0.085, color=X_RED)
        good = Dot(good_point, radius=0.085, color=Y_GREEN)
        bad_line = Line(c,bad_point,color=X_RED,stroke_width=2.2)
        good_line = Line(c,good_point,color=Y_GREEN,stroke_width=2.2)
        card = statement("为什么要归一化？", ["网络输出和浮点累积会偏离单位球", "长度偏离后不再是纯旋转", "", "q_hat = q / ||q||", "零范数必须单独处理"], 5.0, CYAN)
        card.to_edge(RIGHT,buff=0.55).shift(DOWN*0.12)
        tag_bad = label_chip("||q|| ≠ 1", X_RED, mono=True).next_to(bad,RIGHT,buff=0.12)
        tag_good = label_chip("||q_hat|| = 1", Y_GREEN, mono=True).next_to(good,RIGHT,buff=0.12)
        cap = bottom_caption("归一化只修长度，不会替你修正字段顺序或旋转方向。", TEXT)

        self.play(FadeIn(h),Create(circle),FadeIn(card,shift=LEFT*0.12),run_time=0.9)
        self.play(Create(bad_line),FadeIn(bad,tag_bad),run_time=0.8)
        self.play(Transform(bad_line,good_line),Transform(bad,good),Transform(tag_bad,tag_good),run_time=1.2)
        self.play(FadeIn(cap),run_time=0.5)
        self.wait(1.5)
        fade_all(self)

    def double_cover(self):
        add_base(self)
        h = header(3, "DOUBLE COVER", "q 与 −q 是两个坐标点，却代表同一个姿态")
        c = LEFT*2.75+DOWN*0.15
        circle = Circle(2.05,color=LINE,stroke_width=1.5).move_to(c)
        angle=35*DEGREES
        qpos=c+2.05*np.array([np.cos(angle),np.sin(angle),0])
        qneg=c-2.05*np.array([np.cos(angle),np.sin(angle),0])
        q=Dot(qpos,radius=0.09,color=VIOLET)
        nq=Dot(qneg,radius=0.09,color=ORANGE)
        diameter=DashedLine(qneg,qpos,color=MUTED,stroke_width=1.3)
        tq=label_chip("q",VIOLET,mono=True).next_to(q,UR,buff=0.08)
        tnq=label_chip("−q",ORANGE,mono=True).next_to(nq,DL,buff=0.08)
        card=statement("为什么物理结果相同？",["p′ = q ⊗ p ⊗ q⁻¹","把 q 全部取负后","左右两个负号互相抵消","","球面两个对跖点 → 同一个 SO(3) 姿态"],5.2,CYAN)
        card.to_edge(RIGHT,buff=0.48).shift(DOWN*0.12)
        same=formula_bar("q  ~  −q   （同一个三维旋转）",Y_GREEN,size=23).to_edge(DOWN,buff=0.22)

        self.play(FadeIn(h),Create(circle),Create(diameter),run_time=0.8)
        self.play(FadeIn(q,nq,tq,tnq),FadeIn(card,shift=LEFT*0.12),run_time=0.9)
        self.play(FadeIn(same),run_time=0.5)
        self.wait(1.8)
        fade_all(self)

    def composition(self):
        add_base(self)
        h=header(4,"COMPOSITION ORDER","先执行 q₁，再执行 q₂：总旋转为什么反着写？")
        c=LEFT*2.8+DOWN*0.2
        circle=Circle(2.0,color=LINE,stroke_width=1.5).move_to(c)
        v0=orientation_arrow(c,0,1.85,MUTED)
        v1=orientation_arrow(c,35*DEGREES,1.85,Y_GREEN)
        v2=orientation_arrow(c,95*DEGREES,1.85,X_RED)
        arc1=Arc(0.75,0,35*DEGREES,arc_center=c,color=Y_GREEN,stroke_width=2)
        arc2=Arc(1.05,35*DEGREES,60*DEGREES,arc_center=c,color=X_RED,stroke_width=2)
        q1=label_chip("先 q₁ · +35°",Y_GREEN,mono=True).next_to(c+RIGHT*1.5,DOWN,buff=0.18)
        q2=label_chip("再 q₂ · +60°",X_RED,mono=True).next_to(c+UP*1.65,RIGHT,buff=0.12)
        card=statement("与列向量矩阵一致",["右侧操作先作用","先 q₁，再 q₂","","q_total = q₂ ⊗ q₁","通常不可交换"],4.9,CYAN)
        card.to_edge(RIGHT,buff=0.55).shift(DOWN*0.12)
        cap=bottom_caption("乘法顺序必须和主动/被动旋转约定一起记录。",TEXT)

        self.play(FadeIn(h),Create(circle),FadeIn(v0),run_time=0.8)
        self.play(Transform(v0,v1),Create(arc1),FadeIn(q1),run_time=1.0)
        self.play(Transform(v0,v2),Create(arc2),FadeIn(q2),run_time=1.1)
        self.play(FadeIn(card,shift=LEFT*0.12),FadeIn(cap),run_time=0.8)
        self.wait(1.5)
        fade_all(self)

    def slerp(self):
        add_base(self)
        h=header(5,"SLERP · SHORTEST PATH","插值前先看点积，避免在单位球面上绕远路")
        c=LEFT*2.8+DOWN*0.15
        r=2.05
        circle=Circle(r,color=LINE,stroke_width=1.5).move_to(c)
        a0=20*DEGREES;a1=155*DEGREES
        q0=c+r*np.array([np.cos(a0),np.sin(a0),0])
        q1=c+r*np.array([np.cos(a1),np.sin(a1),0])
        nq1=c-r*np.array([np.cos(a1),np.sin(a1),0])
        d0=Dot(q0,radius=0.085,color=CYAN);d1=Dot(q1,radius=0.085,color=X_RED);dn=Dot(nq1,radius=0.085,color=Y_GREEN)
        t0=label_chip("q₀",CYAN,mono=True).next_to(d0,RIGHT,buff=0.08)
        t1=label_chip("q₁",X_RED,mono=True).next_to(d1,LEFT,buff=0.08)
        tn=label_chip("−q₁ · 同一姿态",Y_GREEN,mono=True).next_to(dn,RIGHT,buff=0.08)
        long_arc=Arc(r,a0,a1-a0,arc_center=c,color=X_RED,stroke_width=3).set_fill(opacity=0).set_stroke(opacity=0.65)
        short_angle=((a1+PI)-a0)%(TAU)
        if short_angle>PI: short_angle-=TAU
        short_arc=Arc(r,a0,short_angle,arc_center=c,color=Y_GREEN,stroke_width=3)
        card=statement("最短路径规则",["若 q₀ᵀq₁ < 0","先令 q₁ ← −q₁","物理姿态不变","球面路径变短"],4.8,CYAN)
        card.to_edge(RIGHT,buff=0.55).shift(DOWN*0.12)
        cap=bottom_caption("接近同一点时，通常改用归一化线性插值避免数值不稳定。",TEXT)

        self.play(FadeIn(h),Create(circle),FadeIn(d0,d1,t0,t1),run_time=0.9)
        self.play(Create(long_arc),run_time=1.0)
        self.play(FadeIn(dn,tn),Create(short_arc),long_arc.animate.set_stroke(opacity=0.15),run_time=1.1)
        self.play(FadeIn(card,shift=LEFT*0.12),FadeIn(cap),run_time=0.8)
        self.wait(1.7)
        fade_all(self)

    def recap(self):
        add_base(self)
        h=header(6,"ENGINEERING CHECKLIST","四元数稳定，不代表接口约定可以省略")
        cards=VGroup(
            statement("字段顺序",["wxyz 还是 xyzw", "必须查接口定义"],3.55,VIOLET),
            statement("单位范数",["使用前归一化", "极小范数单独处理"],3.55,Y_GREEN),
            statement("符号分支",["q 与 −q 等价", "比较/插值先统一"],3.55,ORANGE),
        ).arrange(RIGHT,buff=0.30).shift(UP*0.05)
        formula=formula_bar("姿态误差：q_err = q_target ⊗ q_current⁻¹",CYAN,size=21).next_to(cards,DOWN,buff=0.38)
        cap=bottom_caption("最后仍要检查主动/被动旋转、世界系/机体系与乘法顺序。",TEXT)
        self.play(FadeIn(h),LaggedStart(*[FadeIn(c,shift=UP*0.08) for c in cards],lag_ratio=0.16),run_time=1.2)
        self.play(FadeIn(formula),FadeIn(cap),run_time=0.7)
        self.wait(2.5)


class QuaternionSlerpPoster(Scene):
    def construct(self):
        add_base(self)
        h=header(0,"UNIT QUATERNION","半角、双覆盖与最短路径插值")
        c=LEFT*3.6+DOWN*0.1
        circle=Circle(2.05,color=VIOLET,stroke_width=1.8).move_to(c)
        a=35*DEGREES
        q=c+2.05*np.array([np.cos(a),np.sin(a),0]);nq=2*c-q
        dq=Dot(q,radius=0.1,color=VIOLET);dn=Dot(nq,radius=0.1,color=ORANGE)
        diameter=DashedLine(nq,q,color=MUTED,stroke_width=1.3)
        tq=label_chip("q",VIOLET,mono=True).next_to(dq,UR,buff=0.08)
        tn=label_chip("−q",ORANGE,mono=True).next_to(dn,DL,buff=0.08)
        card=statement("三个关键事实",["q = (cos α/2, u·sin α/2)","||q|| = 1","q 与 −q 表示同一旋转","","SLERP 前先选择最短符号分支"],5.5,CYAN)
        card.to_edge(RIGHT,buff=0.50).shift(DOWN*0.10)
        cap=bottom_caption("四元数解决欧拉角奇异，但不会自动解决约定错误。",TEXT)
        self.add(h,circle,diameter,dq,dn,tq,tn,card,cap)
