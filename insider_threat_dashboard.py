import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import plotly.io as pio

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Security Monitor - Insider Threat Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM STYLING
# ============================================
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
        color: #E2E8F0;
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95) !important;
        border-right: 2px solid #38BDF8;
    }

    section[data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }

    h1 {
        color: #38BDF8;
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 0.5em;
        text-shadow: 0px 2px 8px rgba(56, 189, 248, 0.3);
    }

    h2 {
        color: #7DD3FC;
        font-size: 1.8em;
        font-weight: 600;
        margin-top: 0.8em;
        margin-bottom: 0.5em;
    }

    h3 {
        color: #BAE6FD;
        font-size: 1.3em;
        font-weight: 500;
    }

    p, li {
        color: #CBD5E1;
        font-size: 0.95em;
        line-height: 1.6;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 0.95em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0px 4px 12px rgba(14, 165, 233, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0px 6px 16px rgba(14, 165, 233, 0.5) !important;
    }

    .stTextInput input {
        background-color: #1E293B !important;
        color: white !important;
        border: 1.5px solid #334155 !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
    }

    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1E293B 0%, #293548 100%) !important;
        border: 1.5px solid #334155 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

    .stSuccess {
        background-color: rgba(6, 78, 59, 0.4) !important;
        border-left: 4px solid #10B981 !important;
        border-radius: 8px !important;
    }

    .stError {
        background-color: rgba(127, 29, 29, 0.4) !important;
        border-left: 4px solid #EF4444 !important;
        border-radius: 8px !important;
    }

    .stWarning {
        background-color: rgba(120, 53, 15, 0.4) !important;
        border-left: 4px solid #F97316 !important;
        border-radius: 8px !important;
    }

    .stInfo {
        background-color: rgba(3, 102, 214, 0.2) !important;
        border-left: 4px solid #0EA5E9 !important;
        border-radius: 8px !important;
    }

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #0F172A;
    }

    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }

    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #334155, transparent);
        margin: 2em 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE
# ============================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "threat_data" not in st.session_state:
    st.session_state.threat_data = None

# ============================================
# SAMPLE DATA GENERATOR (Replace with your model output)
# ============================================
@st.cache_data
def generate_sample_data():
    """
    REPLACE THIS FUNCTION WITH YOUR TRAINED MODEL OUTPUT
    This function should return a DataFrame with your model's predictions
    """
    np.random.seed(42)
    
    users = [f"USER_{str(i).zfill(4)}" for i in range(1, 51)]
    departments = ["Engineering", "Finance", "HR", "Operations", "Sales"]
    roles = ["Junior Developer", "Senior Analyst", "Manager", "Director", "Contractor"]
    
    data = {
        'user_id': users,
        'department': np.random.choice(departments, 50),
        'role': np.random.choice(roles, 50),
        'total_logons': np.random.randint(5, 200, 50),
        'afterhours_activity': np.random.randint(0, 50, 50),
        'file_transfers': np.random.randint(0, 100, 50),
        'removable_media_usage': np.random.randint(0, 30, 50),
        'abnormal_locations': np.random.randint(0, 10, 50),
        'dnn_score': np.random.uniform(0, 1, 50),
        'cnn_score': np.random.uniform(0, 1, 50),
        'ae_score': np.random.uniform(0, 1, 50),
    }
    
    df = pd.DataFrame(data)
    df['risk_score'] = (df['dnn_score'] + df['cnn_score'] + df['ae_score']) / 3
    
    def assign_threat_level(score):
        if score >= 0.75:
            return "🔴 CRITICAL"
        elif score >= 0.50:
            return "🟠 HIGH"
        elif score >= 0.25:
            return "🟡 MEDIUM"
        else:
            return "🟢 LOW"
    
    df['threat_level'] = df['risk_score'].apply(assign_threat_level)
    df['last_activity'] = [datetime.now() - timedelta(hours=np.random.randint(0, 168)) for _ in range(50)]
    df['status'] = np.random.choice(['Active', 'Inactive', 'Suspicious'], 50)
    
    return df.sort_values('risk_score', ascending=False)

# ============================================
# PDF GENERATION FUNCTION
# ============================================
def generate_pdf_report(threat_data, filters_info):
    """Generate comprehensive PDF report"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0EA5E9'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#38BDF8'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    # Title
    elements.append(Paragraph("🛡️ INSIDER THREAT DETECTION REPORT", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Report info
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Report Generated: {report_date}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    critical_count = len(threat_data[threat_data['risk_score'] >= 0.75])
    high_count = len(threat_data[(threat_data['risk_score'] >= 0.50) & (threat_data['risk_score'] < 0.75)])
    medium_count = len(threat_data[(threat_data['risk_score'] >= 0.25) & (threat_data['risk_score'] < 0.50)])
    low_count = len(threat_data[threat_data['risk_score'] < 0.25])
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Users Monitored', str(len(threat_data))],
        ['Critical Threats (75-100%)', str(critical_count)],
        ['High Risk (50-75%)', str(high_count)],
        ['Medium Risk (25-50%)', str(medium_count)],
        ['Low Risk (0-25%)', str(low_count)],
        ['Average Risk Score', f"{threat_data['risk_score'].mean():.2%}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0EA5E9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Top Risk Users
    elements.append(Paragraph("TOP 10 HIGH-RISK USERS", heading_style))
    
    high_risk_users = threat_data.nlargest(10, 'risk_score')
    risk_data = [['User ID', 'Department', 'Risk Score', 'Threat Level', 'Status']]
    
    for _, user in high_risk_users.iterrows():
        risk_data.append([
            user['user_id'],
            user['department'],
            f"{user['risk_score']:.1%}",
            user['threat_level'],
            user['status']
        ])
    
    risk_table = Table(risk_data, colWidths=[1.2*inch, 1.3*inch, 1.2*inch, 1.2*inch, 1.1*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38BDF8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white]),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Department Analysis
    elements.append(Paragraph("RISK BY DEPARTMENT", heading_style))
    
    dept_risk = threat_data.groupby('department').agg({
        'risk_score': ['mean', 'count']
    }).round(3)
    dept_risk.columns = ['Avg Risk', 'User Count']
    dept_risk = dept_risk.reset_index()
    
    dept_data = [['Department', 'Avg Risk Score', 'User Count']]
    for _, row in dept_risk.iterrows():
        dept_data.append([row['department'], f"{row['Avg Risk']:.1%}", str(int(row['User Count']))])
    
    dept_table = Table(dept_data, colWidths=[2*inch, 2*inch, 2*inch])
    dept_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38BDF8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white]),
    ]))
    elements.append(dept_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Key Findings
    elements.append(Paragraph("KEY FINDINGS", heading_style))
    
    findings = f"""
    • {critical_count} user(s) flagged as CRITICAL threat - immediate investigation recommended<br/>
    • {high_count} user(s) identified as HIGH risk - close monitoring required<br/>
    • Average organizational risk score: {threat_data['risk_score'].mean():.1%}<br/>
    • Most active threat vectors: Removable media usage and after-hours access<br/>
    • Recommended action: Schedule security briefings for high-risk users<br/>
    """
    
    elements.append(Paragraph(findings, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_text = "This report contains confidential information about security threats. Handle with care."
    elements.append(Paragraph(f"<i>{footer_text}</i>", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ============================================
# LOGIN PAGE
# ============================================
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(10px);
            padding: 50px 40px;
            border-radius: 16px;
            border: 1.5px solid #334155;
            box-shadow: 0px 8px 32px rgba(56, 189, 248, 0.15);
            text-align: center;
        '>
        """, unsafe_allow_html=True)
        
        st.markdown("## 🛡️ Security Monitor")
        st.markdown("### Insider Threat Detection System")
        st.markdown("*AI-Powered Threat Analysis & Monitoring*")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        username = st.text_input("👤 Username", placeholder="Enter username", label_visibility="collapsed")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            demo = st.button("📋 Demo Login", use_container_width=True)
        with col_b:
            admin = st.button("🔐 Admin Login", use_container_width=True)
        
        if admin or demo:
            if (username.strip() == "admin" and password.strip() == "admin123") or demo:
                with st.spinner("🔓 Unlocking dashboard..."):
                    time.sleep(1)
                st.session_state.logged_in = True
                st.session_state.username = "Admin" if admin else "Demo User"
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Try admin/admin123 or Demo Login")
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B; font-size: 0.9em;'>Demo: admin / admin123</p>", unsafe_allow_html=True)

# ============================================
# MAIN DASHBOARD
# ============================================
def main_dashboard():
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Dashboard Settings")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"### 👤 {st.session_state.username}")
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
        
        st.divider()
        st.markdown("### 📊 Filters")
        
        department_filter = st.multiselect(
            "Department",
            options=st.session_state.threat_data['department'].unique(),
            default=st.session_state.threat_data['department'].unique()[:2]
        )
        
        risk_filter = st.multiselect(
            "Threat Level",
            options=['🔴 CRITICAL', '🟠 HIGH', '🟡 MEDIUM', '🟢 LOW'],
            default=['🔴 CRITICAL', '🟠 HIGH']
        )
        
        status_filter = st.multiselect(
            "Status",
            options=st.session_state.threat_data['status'].unique(),
            default=st.session_state.threat_data['status'].unique()
        )
        
        st.divider()
        st.markdown("### 📋 Quick Stats")
        total_users = len(st.session_state.threat_data)
        high_risk = len(st.session_state.threat_data[st.session_state.threat_data['risk_score'] >= 0.50])
        critical = len(st.session_state.threat_data[st.session_state.threat_data['risk_score'] >= 0.75])
        
        st.metric("Total Users", total_users)
        st.metric("High Risk Users", high_risk)
        st.metric("Critical Threats", critical)
    
    # Main content
    st.markdown("# 🛡️ Security Monitor Dashboard")
    
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0px 4px 12px rgba(14, 165, 233, 0.3);
    '>
        <h2 style='color: white; margin: 0;'>🚀 Real-time Insider Threat Detection</h2>
        <p style='color: #E0F2FE; margin: 8px 0 0 0;'>Monitor suspicious activities and protect your organization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter data
    filtered_data = st.session_state.threat_data[
        (st.session_state.threat_data['department'].isin(department_filter)) &
        (st.session_state.threat_data['threat_level'].isin(risk_filter)) &
        (st.session_state.threat_data['status'].isin(status_filter))
    ]
    
    # KPI Cards
    st.markdown("## 📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        critical_count = len(st.session_state.threat_data[st.session_state.threat_data['risk_score'] >= 0.75])
        st.metric("🔴 Critical Threats", critical_count, f"{int((critical_count/len(st.session_state.threat_data))*100)}%")
    
    with col2:
        high_count = len(st.session_state.threat_data[(st.session_state.threat_data['risk_score'] >= 0.50) & (st.session_state.threat_data['risk_score'] < 0.75)])
        st.metric("🟠 High Risk", high_count, f"{int((high_count/len(st.session_state.threat_data))*100)}%")
    
    with col3:
        avg_risk = st.session_state.threat_data['risk_score'].mean()
        st.metric("📊 Avg Risk Score", f"{avg_risk:.2%}", "Overall posture")
    
    with col4:
        suspicious = len(st.session_state.threat_data[st.session_state.threat_data['status'] == 'Suspicious'])
        st.metric("⚠️ Suspicious Activity", suspicious, "Requires action")
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "👥 Users",
        "📈 Analytics",
        "🔍 Details",
        "📄 Export"
    ])
    
    # TAB 1: Dashboard
    with tab1:
        st.markdown("## Risk Distribution Overview")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Risk distribution bar chart
            risk_counts = {
                'CRITICAL': len(st.session_state.threat_data[st.session_state.threat_data['risk_score'] >= 0.75]),
                'HIGH': len(st.session_state.threat_data[(st.session_state.threat_data['risk_score'] >= 0.50) & (st.session_state.threat_data['risk_score'] < 0.75)]),
                'MEDIUM': len(st.session_state.threat_data[(st.session_state.threat_data['risk_score'] >= 0.25) & (st.session_state.threat_data['risk_score'] < 0.50)]),
                'LOW': len(st.session_state.threat_data[st.session_state.threat_data['risk_score'] < 0.25])
            }
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(risk_counts.keys()),
                    y=list(risk_counts.values()),
                    marker=dict(
                        color=['#EF4444', '#F97316', '#EAB308', '#22C55E'],
                        line=dict(color='#334155', width=2)
                    ),
                    text=list(risk_counts.values()),
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Users: %{y}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title="User Distribution by Risk Level",
                xaxis_title="Risk Level",
                yaxis_title="Number of Users",
                plot_bgcolor='rgba(15, 23, 42, 0.5)',
                paper_bgcolor='rgba(15, 23, 42, 0)',
                font=dict(color='#E2E8F0'),
                height=400,
                showlegend=False,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Threat Guide")
            st.markdown("""
            **🔴 CRITICAL (75-100%)**
            Immediate action needed
            
            **🟠 HIGH (50-75%)**
            Monitor closely
            
            **🟡 MEDIUM (25-50%)**
            Regular review
            
            **🟢 LOW (0-25%)**
            Standard monitoring
            """)
        
        st.markdown("---")
        
        # Donut chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Critical', 'High', 'Medium', 'Low'],
                values=list(risk_counts.values()),
                marker=dict(colors=['#EF4444', '#F97316', '#EAB308', '#22C55E']),
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
            )])
            
            fig_pie.update_layout(
                title="Risk Level Breakdown",
                plot_bgcolor='rgba(15, 23, 42, 0)',
                paper_bgcolor='rgba(15, 23, 42, 0)',
                font=dict(color='#E2E8F0'),
                height=400
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Department distribution
            dept_data = st.session_state.threat_data['department'].value_counts()
            
            fig_dept = go.Figure(data=[go.Bar(
                x=dept_data.index,
                y=dept_data.values,
                marker=dict(
                    color=dept_data.values,
                    colorscale='Blues',
                    showscale=False,
                    line=dict(color='#334155', width=2)
                ),
                text=dept_data.values,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Users: %{y}<extra></extra>'
            )])
            
            fig_dept.update_layout(
                title="Users by Department",
                xaxis_title="Department",
                yaxis_title="Count",
                plot_bgcolor='rgba(15, 23, 42, 0.5)',
                paper_bgcolor='rgba(15, 23, 42, 0)',
                font=dict(color='#E2E8F0'),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_dept, use_container_width=True)
    
    # TAB 2: Users
    with tab2:
        st.markdown("## User Risk Profile")
        
        display_data = filtered_data[[
            'user_id', 'department', 'role', 'threat_level',
            'risk_score', 'status', 'afterhours_activity',
            'removable_media_usage'
        ]].copy()
        
        display_data['risk_score'] = display_data['risk_score'].apply(lambda x: f"{x:.1%}")
        
        st.dataframe(
            display_data.sort_values('risk_score', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    # TAB 3: Analytics
    with tab3:
        st.markdown("## Detailed Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk score histogram
            fig_hist = go.Figure(data=[go.Histogram(
                x=st.session_state.threat_data['risk_score'],
                nbinsx=15,
                marker=dict(
                    color='#0EA5E9',
                    line=dict(color='#334155', width=1)
                ),
                hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
            )])
            
            fig_hist.update_layout(
                title="Risk Score Distribution",
                xaxis_title="Risk Score",
                yaxis_title="Number of Users",
                plot_bgcolor='rgba(15, 23, 42, 0.5)',
                paper_bgcolor='rgba(15, 23, 42, 0)',
                font=dict(color='#E2E8F0'),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Department risk analysis
            dept_risk = st.session_state.threat_data.groupby('department')['risk_score'].mean().sort_values(ascending=False)
            
            fig_dept_risk = go.Figure(data=[go.Bar(
                x=dept_risk.index,
                y=dept_risk.values,
                marker=dict(
                    color=dept_risk.values,
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Avg Risk")
                ),
                text=[f"{v:.1%}" for v in dept_risk.values],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Avg Risk: %{y:.1%}<extra></extra>'
            )])
            
            fig_dept_risk.update_layout(
                title="Average Risk by Department",
                xaxis_title="Department",
                yaxis_title="Average Risk Score",
                plot_bgcolor='rgba(15, 23, 42, 0.5)',
                paper_bgcolor='rgba(15, 23, 42, 0)',
                font=dict(color='#E2E8F0'),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_dept_risk, use_container_width=True)
        
        # Activity correlations
        col1, col2 = st.columns(2)
        
        with col1:
            # After-hours vs Risk
            fig_activity = go.Figure(data=[go.Scatter(
                x=st.session_state.threat_data['afterhours_activity'],
                y=st.session_state.threat_data['risk_score'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=st.session_state.threat_data['risk_score'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Risk Score"),
                    line=dict(color='#334155', width=1)
                ),
                text=st.session_state.threat_data['user_id'],
                hovertemplate='<b>%{text}</b><br>After-hours: %{x}<br>Risk: %{y:.1%}<extra></extra>'
            )])
            
            fig_activity.update_layout(
                title="After-hours Activity vs Risk",
                xaxis_title="After-hours Activity Count",
                yaxis_title="Risk Score",
                plot_bgcolor='rgba(15, 23, 42, 0.5)',
                paper_bgcolor='rgba(15, 23, 42, 0)',
                font=dict(color='#E2E8F0'),
                height=400
            )
            
            st.plotly_chart(fig_activity, use_container_width=True)
        
        with col2:
            # USB vs Risk
            fig_usb = go.Figure(data=[go.Scatter(
                x=st.session_state.threat_data['removable_media_usage'],
                y=st.session_state.threat_data['risk_score'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=st.session_state.threat_data['risk_score'],
                    colorscale='Oranges',
                    showscale=True,
                    colorbar=dict(title="Risk Score"),
                    line=dict(color='#334155', width=1)
                ),
                text=st.session_state.threat_data['user_id'],
                hovertemplate='<b>%{text}</b><br>USB Usage: %{x}<br>Risk: %{y:.1%}<extra></extra>'
            )])
            
            fig_usb.update_layout(
                title="USB/Removable Media vs Risk",
                xaxis_title="Removable Media Usage Count",
                yaxis_title="Risk Score",
                plot_bgcolor='rgba(15, 23, 42, 0.5)',
                paper_bgcolor='rgba(15, 23, 42, 0)',
                font=dict(color='#E2E8F0'),
                height=400
            )
            
            st.plotly_chart(fig_usb, use_container_width=True)
    
    # TAB 4: Deep Dive
    with tab4:
        st.markdown("## 🔍 High-Risk User Profiles")
        
        high_risk_users = st.session_state.threat_data[
            st.session_state.threat_data['risk_score'] >= 0.50
        ].sort_values('risk_score', ascending=False)
        
        if len(high_risk_users) > 0:
            for idx, (_, user) in enumerate(high_risk_users.head(10).iterrows()):
                with st.expander(f"📋 {user['user_id']} - {user['threat_level']} | Risk: {user['risk_score']:.1%}", expanded=idx==0):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**👤 User Information**")
                        st.write(f"🏢 Department: {user['department']}")
                        st.write(f"💼 Role: {user['role']}")
                        st.write(f"⚡ Status: {user['status']}")
                    
                    with col2:
                        st.write("**📊 Activity Metrics**")
                        st.write(f"🔓 Total Logons: {user['total_logons']}")
                        st.write(f"🌙 After-hours: {user['afterhours_activity']}")
                        st.write(f"💾 USB Usage: {user['removable_media_usage']}")
                    
                    with col3:
                        st.write("**🎯 Risk Scores**")
                        st.write(f"**Overall: {user['risk_score']:.1%}**")
                        st.write(f"DNN: {user['dnn_score']:.1%}")
                        st.write(f"CNN: {user['cnn_score']:.1%}")
                    
                    # Progress bar
                    st.progress(user['risk_score'], text=f"Risk Level: {user['risk_score']:.1%}")
        else:
            st.info("✅ No high-risk users in current filters")
    
    # TAB 5: Export
    with tab5:
        st.markdown("## 📄 Report Generation & Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Generate PDF Report")
            if st.button("📥 Generate Full PDF Report", use_container_width=True):
                with st.spinner("Generating PDF report..."):
                    pdf_buffer = generate_pdf_report(
                        st.session_state.threat_data,
                        {
                            'departments': department_filter,
                            'risk_levels': risk_filter,
                            'statuses': status_filter
                        }
                    )
                    
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_buffer,
                        file_name=f"threat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.success("✅ PDF report ready for download!")
        
        with col2:
            st.markdown("### Export as CSV")
            if st.button("📥 Export to CSV", use_container_width=True):
                csv = st.session_state.threat_data.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"threat_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success("✅ CSV ready for download!")
        
        st.divider()
        
        st.markdown("### Report Preview")
        st.info("📄 Click buttons above to download PDF or CSV reports with complete threat analysis data")
        
        # Show sample data
        st.markdown("**Sample Data Structure:**")
        sample = st.session_state.threat_data.head(3)[['user_id', 'department', 'role', 'risk_score', 'threat_level', 'status']]
        st.dataframe(sample, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: #64748B; padding: 20px; font-size: 0.9em;'>
        <p>🛡️ <b>Security Monitor Dashboard</b> | Insider Threat Detection System</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# ============================================
# APP ENTRY
# ============================================
if st.session_state.logged_in:
    if st.session_state.threat_data is None:
        st.session_state.threat_data = generate_sample_data()
    main_dashboard()
else:
    login_page()
