%% This is file `saucis.cls',
%% 19.11.2025 tarihinde Prof.Dr. Ahmet Zengin tarafından oluşturulmuştur. 
%% elsarticle temel alınarak geliştirildi. 
%% stil ile ilgili satırlar 627 den başlıyor

\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{saucis} [2025/11/18 v1.0 Non Standard LaTeX document class]

\newcommand\@ptsize{}
\newif\if@restonecol
\newif\if@titlepage
\@titlepagefalse
\DeclareOption{a4paper}
   {\setlength\paperheight {297mm}%
    \setlength\paperwidth  {210mm}}
\DeclareOption{a5paper}
   {\setlength\paperheight {210mm}%
    \setlength\paperwidth  {148mm}}
\DeclareOption{b5paper}
   {\setlength\paperheight {250mm}%
    \setlength\paperwidth  {176mm}}
\DeclareOption{letterpaper}
   {\setlength\paperheight {11in}%
    \setlength\paperwidth  {8.5in}}
\DeclareOption{legalpaper}
   {\setlength\paperheight {14in}%
    \setlength\paperwidth  {8.5in}}
\DeclareOption{executivepaper}
   {\setlength\paperheight {10.5in}%
    \setlength\paperwidth  {7.25in}}
\DeclareOption{landscape}
   {\setlength\@tempdima   {\paperheight}%
    \setlength\paperheight {\paperwidth}%
    \setlength\paperwidth  {\@tempdima}}
\DeclareOption{8pt}{\renewcommand\@ptsize{8}}
\DeclareOption{9pt}{\renewcommand\@ptsize{9}}
\DeclareOption{10pt}{\renewcommand\@ptsize{10}}
\DeclareOption{11pt}{\renewcommand\@ptsize{11}}
\DeclareOption{12pt}{\renewcommand\@ptsize{12}}
\DeclareOption{14pt}{\renewcommand\@ptsize{14}}
\DeclareOption{17pt}{\renewcommand\@ptsize{17}}
\DeclareOption{20pt}{\renewcommand\@ptsize{20}}
\DeclareOption{oneside}{\@twosidefalse \@mparswitchfalse}
\DeclareOption{twoside}{\@twosidetrue  \@mparswitchtrue}
\DeclareOption{draft}{\setlength\overfullrule{5pt}}
\DeclareOption{final}{\setlength\overfullrule{0pt}}
\DeclareOption{titlepage}{\@titlepagetrue}
\DeclareOption{notitlepage}{\@titlepagefalse}
\DeclareOption{onecolumn}{\@twocolumnfalse}
\DeclareOption{twocolumn}{\@twocolumntrue}
\DeclareOption{leqno}{\input{leqno.clo}}
\DeclareOption{fleqn}{\input{fleqn.clo}}
\DeclareOption{openbib}{%
  \AtEndOfPackage{%
   \renewcommand\@openbib@code{%
      \advance\leftmargin\bibindent
      \itemindent -\bibindent
      \listparindent \itemindent
      \parsep \z@
      }%
   \renewcommand\newblock{\par}}%
}
%\ExecuteOptions{letterpaper,9pt,twocolumn,final}
\ProcessOptions
\def\EC@family#1#2#3#4#5{%
  \DeclareFontShape{#1}{#2}{#3}{#4}%
  {<5><6><7><8><9><10><10.95><12><14.4>%
   <17.28><20.74><24.88><29.86><35.83><42.99><51.59>genb*#5}{}}
\EC@family{T1}{cmr}{m}{n}{ecrm}
\EC@family{T1}{cmr}{m}{sl}{ecsl}
\EC@family{T1}{cmr}{m}{it}{ecti}
\EC@family{T1}{cmr}{m}{sc}{eccc}
\EC@family{T1}{cmr}{bx}{n}{ecbx}
\EC@family{T1}{cmr}{b}{n}{ecrb}
\EC@family{T1}{cmr}{bx}{it}{ecbi}
\EC@family{T1}{cmr}{bx}{sl}{ecbl}
\EC@family{T1}{cmr}{bx}{sc}{ecxc}
\EC@family{T1}{cmr}{m}{ui}{ecui}
\DeclareFontShape{OT1}{cmr}{m}{n}%
     {<5><6><7><8><9><10><12>gen*cmr%
      <10.95>cmr10%
      <14.4>cmr12%
      <17.28><20.74><24.88><29.86><35.83><42.99><51.59>cmr17}{}
\DeclareFontShape{OT1}{cmr}{m}{sl}%
     {<5><6><7>cmsl8%
      <8><9>gen*cmsl%
      <10><10.95>cmsl10%
      <12><14.4><17.28><20.74><24.88><29.86><35.83><42.99><51.59>cmsl12%
      }{}
\DeclareFontShape{OT1}{cmr}{m}{it}%
     {<5><6><7>cmti7%
      <8>cmti8%
      <9>cmti9%
      <10><10.95>cmti10%
      <12><14.4><17.28><20.74><24.88><29.86><35.83><42.99><51.59>cmti12%
      }{}
\DeclareFontShape{OT1}{cmr}{m}{sc}%
     {<5><6><7><8><9><10><10.95><12>%
      <14.4><17.28><20.74><24.88><29.86><35.83><42.99><51.59>cmcsc10%
      }{}
\DeclareFontShape{OT1}{cmr}{m}{ui}
   {<5><6><7><8><9><10><10.95><12>%
      <14.4><17.28><20.74><24.88><29.86><35.83><42.99><51.59>cmu10%
      }{}
\DeclareFontShape{OT1}{cmr}{b}{n}
     {<5><6><7><8><9><10><10.95><12>%
      <14.4><17.28><20.74><24.88><29.86><35.83><42.99><51.59>cmb10%
      }{}
\DeclareFontShape{OT1}{cmr}{bx}{n}
   {<5><6><7><8><9>gen*cmbx%
      <10><10.95>cmbx10%
      <12><14.4><17.28><20.74><24.88><29.86><35.83><42.99><51.59>cmbx12%
      }{}
\DeclareFontShape{OT1}{cmr}{bx}{sl}
      {<5><6><7><8><9>%
      <10><10.95><12><14.4><17.28><20.74><24.88><29.86><35.83><42.99><51.59>cmbxsl10%
      }{}
\DeclareFontShape{OT1}{cmr}{bx}{it}
      {<5><6><7><8><9>%
      <10><10.95><12><14.4><17.28><20.74><24.88><29.86><35.83><42.99><51.59>cmbxti10%
      }{}
\input{size\@ptsize.clo}
\RequirePackage{exscale}
\setlength\lineskip{1\p@}
\setlength\normallineskip{1\p@}
\renewcommand\baselinestretch{}
\setlength\parskip{0\p@ \@plus \p@}
\@lowpenalty   51
\@medpenalty  151
\@highpenalty 301
\setcounter{topnumber}{2}
\renewcommand\topfraction{.7}
\setcounter{bottomnumber}{1}
\renewcommand\bottomfraction{.3}
\setcounter{totalnumber}{3}
\renewcommand\textfraction{.2}
\renewcommand\floatpagefraction{.5}
\setcounter{dbltopnumber}{2}
\renewcommand\dbltopfraction{.7}
\renewcommand\dblfloatpagefraction{.5}
\if@twoside
  \def\ps@headings{%
      \let\@oddfoot\@empty\let\@evenfoot\@empty
      \def\@evenhead{\thepage\hfil\slshape\leftmark}%
      \def\@oddhead{{\slshape\rightmark}\hfil\thepage}%
      \let\@mkboth\markboth
    \def\sectionmark##1{%
      \markboth {\MakeUppercase{%
        \ifnum \c@secnumdepth >\z@
          \thesection\quad
        \fi
        ##1}}{}}%
    \def\subsectionmark##1{%
      \markright {%
        \ifnum \c@secnumdepth >\@ne
          \thesubsection\quad
        \fi
        ##1}}}
\else
  \def\ps@headings{%
    \let\@oddfoot\@empty
    \def\@oddhead{{\slshape\rightmark}\hfil\thepage}%
    \let\@mkboth\markboth
    \def\sectionmark##1{%
      \markright {\MakeUppercase{%
        \ifnum \c@secnumdepth >\m@ne
          \thesection\quad
        \fi
        ##1}}}}
\fi
\def\ps@myheadings{%
    \let\@oddfoot\@empty\let\@evenfoot\@empty
    \def\@evenhead{\thepage\hfil\slshape\leftmark}%
    \def\@oddhead{{\slshape\rightmark}\hfil\thepage}%
    \let\@mkboth\@gobbletwo
    \let\sectionmark\@gobble
    \let\subsectionmark\@gobble
    }
  \if@titlepage
  \newcommand\maketitle{\begin{titlepage}%
  \let\footnotesize\small
  \let\footnoterule\relax
  \let \footnote \thanks
  \null\vfil
  \vskip 60\p@
  \begin{center}%
    {\LARGE \@title \par}%
    \vskip 3em%
    {\large
     \lineskip .75em%
      \begin{tabular}[t]{c}%
        \@author
      \end{tabular}\par}%
      \vskip 1.5em%
    {\large \@date \par}%       % Set date in \large size.
  \end{center}\par
  \@thanks
  \vfil\null
  \end{titlepage}%
  \setcounter{footnote}{0}%
  \global\let\thanks\relax
  \global\let\maketitle\relax
  \global\let\@thanks\@empty
  \global\let\@author\@empty
  \global\let\@date\@empty
  \global\let\@title\@empty
  \global\let\title\relax
  \global\let\author\relax
  \global\let\date\relax
  \global\let\and\relax
}
\else
\newcommand\maketitle{\par
  \begingroup
    \renewcommand\thefootnote{\@fnsymbol\c@footnote}%
    \def\@makefnmark{\rlap{\@textsuperscript{\normalfont\@thefnmark}}}%
    \long\def\@makefntext##1{\parindent 1em\noindent
            \hb@xt@1.8em{%
                \hss\@textsuperscript{\normalfont\@thefnmark}}##1}%
    \if@twocolumn
      \ifnum \col@number=\@ne
        \@maketitle
      \else
        \twocolumn[\@maketitle]%
      \fi
    \else
      \newpage
      \global\@topnum\z@   % Prevents figures from going at top of page.
      \@maketitle
    \fi
    \thispagestyle{plain}\@thanks
  \endgroup
  \setcounter{footnote}{0}%
  \global\let\thanks\relax
  \global\let\maketitle\relax
  \global\let\@maketitle\relax
  \global\let\@thanks\@empty
  \global\let\@author\@empty
  \global\let\@date\@empty
  \global\let\@title\@empty
  \global\let\title\relax
  \global\let\author\relax
  \global\let\date\relax
  \global\let\and\relax
}
\def\@maketitle{%
  \newpage
  \null
  \vskip 2em%
  \begin{center}%
  \let \footnote \thanks
    {\LARGE \@title \par}%
    \vskip 1.5em%
    {\large
      \lineskip .5em%
      \begin{tabular}[t]{c}%
        \@author
      \end{tabular}\par}%
    \vskip 1em%
    {\large \@date}%
  \end{center}%
  \par
  \vskip 1.5em}
\fi
\setcounter{secnumdepth}{3}
\newcounter {part}
\newcounter {section}
\newcounter {subsection}[section]
\newcounter {subsubsection}[subsection]
\newcounter {paragraph}[subsubsection]
\newcounter {subparagraph}[paragraph]
\renewcommand\thepart         {\@Roman\c@part}
\renewcommand\thesection      {\@arabic\c@section}
\renewcommand\thesubsection   {\thesection.\@arabic\c@subsection}
\renewcommand\thesubsubsection{\thesubsection .\@arabic\c@subsubsection}
\renewcommand\theparagraph    {\thesubsubsection.\@arabic\c@paragraph}
\renewcommand\thesubparagraph {\theparagraph.\@arabic\c@subparagraph}
\newcommand\part{%
   \if@noskipsec \leavevmode \fi\par
   \addvspace{4ex}%
   \@afterindentfalse
   \secdef\@part\@spart}

\def\@part[#1]#2{%
    \ifnum \c@secnumdepth >\m@ne
      \refstepcounter{part}%
      \addcontentsline{toc}{part}{\thepart\hspace{1em}#1}%
    \else
      \addcontentsline{toc}{part}{#1}%
    \fi
    {\parindent \z@ \raggedright
     \interlinepenalty \@M
     \normalfont
     \ifnum \c@secnumdepth >\m@ne
       \Large\bfseries \partname~\thepart
       \par\nobreak
     \fi
     \huge \bfseries #2%
     \markboth{}{}\par}%
    \nobreak
    \vskip 3ex
    \@afterheading}
\def\@spart#1{%
    {\parindent \z@ \raggedright
     \interlinepenalty \@M
     \normalfont
     \huge \bfseries #1\par}%
     \nobreak
     \vskip 3ex
     \@afterheading}
     
\newcommand\section{\@startsection {section}{1}{\z@}%
                                   {-3.5ex \@plus -1ex \@minus -.2ex}%
                                   {2.3ex \@plus.2ex}%
                                   {\normalfont\Large\bfseries} }
\newcommand\subsection{\@startsection{subsection}{2}{\z@}%
                                     {-3.25ex\@plus -1ex \@minus -.2ex}%
                                     {1.5ex \@plus .2ex}%
                                     {\normalfont\large\bfseries}}
\newcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%
                                     {-3.25ex\@plus -1ex \@minus -.2ex}%
                                     {1.5ex \@plus .2ex}%
                                     {\normalfont\normalsize\bfseries}}
\newcommand\paragraph{\@startsection{paragraph}{4}{\z@}%
                                    {3.25ex \@plus1ex \@minus.2ex}%
                                    {-1em}%
                                    {\normalfont\normalsize\bfseries}}
\newcommand\subparagraph{\@startsection{subparagraph}{5}{\parindent}%
                                       {3.25ex \@plus1ex \@minus .2ex}%
                                       {-1em}%
                                      {\normalfont\normalsize\bfseries}}
\if@twocolumn
  \setlength\leftmargini  {2em}
\else
  \setlength\leftmargini  {2.5em}
\fi
\leftmargin  \leftmargini
\setlength\leftmarginii  {2.2em}
\setlength\leftmarginiii {1.87em}
\setlength\leftmarginiv  {1.7em}
\if@twocolumn
  \setlength\leftmarginv  {.5em}
  \setlength\leftmarginvi {.5em}
\else
  \setlength\leftmarginv  {1em}
  \setlength\leftmarginvi {1em}
\fi
\setlength  \labelsep  {.5em}
\setlength  \labelwidth{\leftmargini}
\addtolength\labelwidth{-\labelsep}
\@beginparpenalty -\@lowpenalty
\@endparpenalty   -\@lowpenalty
\@itempenalty     -\@lowpenalty
\renewcommand\theenumi{\@arabic\c@enumi}
\renewcommand\theenumii{\@alph\c@enumii}
\renewcommand\theenumiii{\@roman\c@enumiii}
\renewcommand\theenumiv{\@Alph\c@enumiv}
\newcommand\labelenumi{\theenumi.}
\newcommand\labelenumii{(\theenumii)}
\newcommand\labelenumiii{\theenumiii.}
\newcommand\labelenumiv{\theenumiv.}
\renewcommand\p@enumii{\theenumi}
\renewcommand\p@enumiii{\theenumi(\theenumii)}
\renewcommand\p@enumiv{\p@enumiii\theenumiii}
\newcommand\labelitemi{\textbullet}                       
\newcommand\labelitemii{\normalfont\bfseries \textendash}
\newcommand\labelitemiii{\textasteriskcentered}          
\newcommand\labelitemiv{\textperiodcentered}             
\newenvironment{description}
               {\list{}{\labelwidth\z@ \itemindent-\leftmargin
                        \let\makelabel\descriptionlabel}}
               {\endlist}
\newcommand*\descriptionlabel[1]{\hspace\labelsep
                                \normalfont\bfseries #1}
\if@titlepage
  \newenvironment{abstract}{%
      \titlepage
      \null\vfil
      \@beginparpenalty\@lowpenalty
      \begin{center}%
        \bfseries \abstractname
        \@endparpenalty\@M
      \end{center}}%
     {\par\vfil\null\endtitlepage}
\else
  \newenvironment{abstract}{%
      \if@twocolumn
        \section*{\abstractname}%
      \else
        \small
        \begin{center}%
          {\bfseries \abstractname\vspace{-.5em}\vspace{\z@}}%
        \end{center}%
        \quotation
      \fi}
      {\if@twocolumn\else\endquotation\fi}
\fi
\newenvironment{verse}
               {\let\@centercr
                \list{}{\itemsep      \z@
                        \itemindent   -1.5em%
                        \listparindent\itemindent
                        \rightmargin  \leftmargin
                        \advance\leftmargin 1.5em}%
                \item\relax}
               {\endlist}
\newenvironment{quotation}
               {\list{}{\listparindent 1.5em%
                        \itemindent    \listparindent
                        \rightmargin   \leftmargin
                        \parsep        \z@ \@plus\p@}%
                \item\relax}
               {\endlist}
\newenvironment{quote}
               {\list{}{\rightmargin\leftmargin}%
                \item\relax}
               {\endlist}
\newenvironment{titlepage}
    {%
      \if@twocolumn
        \@restonecoltrue\onecolumn
      \else
        \@restonecolfalse\newpage
      \fi
      \thispagestyle{empty}%
      \setcounter{page}\@ne
    }%
    {\if@restonecol\twocolumn \else \newpage \fi
     \if@twoside\else
        \setcounter{page}\@ne
     \fi
    }
\newcommand\appendix{\par
  \setcounter{section}{0}%
  \setcounter{subsection}{0}%
  \gdef\thesection{\@Alph\c@section}}
\setlength\arraycolsep{5\p@}
\setlength\tabcolsep{6\p@}
\setlength\arrayrulewidth{.4\p@}
\setlength\doublerulesep{2\p@}
\setlength\tabbingsep{\labelsep}
\skip\@mpfootins = \skip\footins
\setlength\fboxsep{3\p@}
\setlength\fboxrule{.4\p@}
\renewcommand\theequation{\@arabic\c@equation}
\newcounter{figure}
\gdef\thefigure{\@arabic\c@figure}
\def\fps@figure{tbp}
\def\ftype@figure{1}
\def\ext@figure{lof}
\def\fnum@figure{\figurename~\thefigure}
\newenvironment{figure}
               {\@float{figure}}
               {\end@float}
\newenvironment{figure*}
               {\@dblfloat{figure}}
               {\end@dblfloat}
\newcounter{table}
\gdef\thetable{\@arabic\c@table}
\def\fps@table{tbp}
\def\ftype@table{2}
\def\ext@table{lot}
\def\fnum@table{\tablename~\thetable}
\newenvironment{table}
               {\@float{table}}
               {\end@float}
\newenvironment{table*}
               {\@dblfloat{table}}
               {\end@dblfloat}
\newlength\abovecaptionskip
\newlength\belowcaptionskip
\setlength\abovecaptionskip{10\p@}
\setlength\belowcaptionskip{0\p@}
\long\def\@makecaption#1#2{%
  \vskip\abovecaptionskip
  \sbox\@tempboxa{#1: #2}%
  \ifdim \wd\@tempboxa >\hsize
    #1: #2\par
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip}
\DeclareOldFontCommand{\rm}{\normalfont\rmfamily}{\mathrm}
\DeclareOldFontCommand{\sf}{\normalfont\sffamily}{\mathsf}
\DeclareOldFontCommand{\tt}{\normalfont\ttfamily}{\mathtt}
\DeclareOldFontCommand{\bf}{\normalfont\bfseries}{\mathbf}
\DeclareOldFontCommand{\it}{\normalfont\itshape}{\mathit}
\DeclareOldFontCommand{\sl}{\normalfont\slshape}{\@nomath\sl}
\DeclareOldFontCommand{\sc}{\normalfont\scshape}{\@nomath\sc}
\DeclareRobustCommand*\cal{\@fontswitch\relax\mathcal}
\DeclareRobustCommand*\mit{\@fontswitch\relax\mathnormal}
\newcommand\@pnumwidth{1.55em}
\newcommand\@tocrmarg{2.55em}
\newcommand\@dotsep{4.5}
\setcounter{tocdepth}{3}
\newcommand\tableofcontents{%
    \section*{\contentsname
        \@mkboth{%
           \MakeUppercase\contentsname}{\MakeUppercase\contentsname}}%
    \@starttoc{toc}%
    }
\newcommand*\l@part[2]{%
  \ifnum \c@tocdepth >-2\relax
    \addpenalty\@secpenalty
    \addvspace{2.25em \@plus\p@}%
    \begingroup
      \setlength\@tempdima{3em}%
      \parindent \z@ \rightskip \@pnumwidth
      \parfillskip -\@pnumwidth
      {\leavevmode
       \large \bfseries #1\hfil \hb@xt@\@pnumwidth{\hss #2}}\par
       \nobreak
    \endgroup
  \fi}
\newcommand*\l@section[2]{%
  \ifnum \c@tocdepth >\z@
    \addpenalty\@secpenalty
    \addvspace{1.0em \@plus\p@}%
    \setlength\@tempdima{1.5em}%
    \begingroup
      \parindent \z@ \rightskip \@pnumwidth
      \parfillskip -\@pnumwidth
      \leavevmode \bfseries
      \advance\leftskip\@tempdima
      \hskip -\leftskip
      #1\nobreak\hfil \nobreak\hb@xt@\@pnumwidth{\hss #2}\par
    \endgroup
  \fi}
\newcommand*\l@subsection{\@dottedtocline{2}{1.5em}{2.3em}}
\newcommand*\l@subsubsection{\@dottedtocline{3}{3.8em}{3.2em}}
\newcommand*\l@paragraph{\@dottedtocline{4}{7.0em}{4.1em}}
\newcommand*\l@subparagraph{\@dottedtocline{5}{10em}{5em}}
\newcommand\listoffigures{%
    \section*{\listfigurename
      \@mkboth{\MakeUppercase\listfigurename}%
              {\MakeUppercase\listfigurename}}%
    \@starttoc{lof}%
    }
\newcommand*\l@figure{\@dottedtocline{1}{1.5em}{2.3em}}
\newcommand\listoftables{%
    \section*{\listtablename
      \@mkboth{%
          \MakeUppercase\listtablename}{\MakeUppercase\listtablename}}%
    \@starttoc{lot}%
    }
\let\l@table\l@figure
\newdimen\bibindent
\setlength\bibindent{1.5em}
\newenvironment{thebibliography}[1]
     {\section*{\refname
        \@mkboth{\MakeUppercase\refname}{\MakeUppercase\refname}}%
      \list{\@biblabel{\@arabic\c@enumiv}}%
           {\settowidth\labelwidth{\@biblabel{#1}}%
            \leftmargin\labelwidth
            \advance\leftmargin\labelsep
            \@openbib@code
            \usecounter{enumiv}%
            \let\p@enumiv\@empty
            \renewcommand\theenumiv{\@arabic\c@enumiv}}%
      \sloppy\clubpenalty4000\widowpenalty4000%
      \sfcode`\.\@m}
     {\def\@noitemerr
       {\@latex@warning{Empty `thebibliography' environment}}%
      \endlist}
\newcommand\newblock{\hskip .11em\@plus.33em\@minus.07em}
\let\@openbib@code\@empty
\newenvironment{theindex}
               {\if@twocolumn
                  \@restonecolfalse
                \else
                  \@restonecoltrue
                \fi
                \columnseprule \z@
                \columnsep 35\p@
                \twocolumn[\section*{\indexname}]%
                \@mkboth{\MakeUppercase\indexname}%
                        {\MakeUppercase\indexname}%
                \thispagestyle{plain}\parindent\z@
                \parskip\z@ \@plus .3\p@\relax
                \let\item\@idxitem}
               {\if@restonecol\onecolumn\else\clearpage\fi}
\newcommand\@idxitem{\par\hangindent 40\p@}
\newcommand\subitem{\@idxitem \hspace*{20\p@}}
\newcommand\subsubitem{\@idxitem \hspace*{30\p@}}
\newcommand\indexspace{\par \vskip 10\p@ \@plus5\p@ \@minus3\p@\relax}
\renewcommand\footnoterule{%
  \kern-3\p@
  \hrule\@width.4\columnwidth
  \kern2.6\p@}
\newcommand\@makefntext[1]{%
    \parindent 1em%
    \noindent
    \hb@xt@1.8em{\hss\@makefnmark}#1}
\newcommand\contentsname{Contents}
\newcommand\listfigurename{List of Figures}
\newcommand\listtablename{List of Tables}
\newcommand\refname{References}
\newcommand\indexname{Index}
\newcommand\figurename{Figure}
\newcommand\tablename{Table}
\newcommand\partname{Part}
\newcommand\appendixname{Appendix}
\newcommand\abstractname{Abstract}
\newcommand\today{\ifcase\month\or
  January\or February\or March\or April\or May\or June\or
  July\or August\or September\or October\or November\or December\fi
  \space\number\day, \number\year}
\setlength\columnsep{10\p@}
\setlength\columnseprule{0\p@}
\pagestyle{plain}
\pagenumbering{arabic}
\if@twoside
\else
  \raggedbottom
\fi
\if@twocolumn
  \twocolumn
  \sloppy
  \flushbottom
\else
  \onecolumn
  
\fi
\def\title#1{\gdef\@title{#1}\gdef\THETITLE{#1}}
%\endinput
%% bu kısım stil ile ilgili komutların başlangıcı!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1

%\ProvidesPackage{saucis}
\usepackage[a4paper,left=1.5cm,right=1.5cm,top=1in,bottom=2cm,asymmetric]{geometry}
\usepackage{ragged2e}
%\usepackage{parskip}
\usepackage[utf8]{inputenc}
\usepackage{mathptmx} %Font.
\usepackage[fleqn]{amsmath} %Equations.
\usepackage[table]{xcolor} %Colored table.
\usepackage{authblk} %Authors' block.
\renewcommand\Authand{, }
\renewcommand\Authands{, }
\usepackage{fancyhdr} %Headers and footers.
\usepackage{enumitem} %Custom list labels.
\usepackage{microtype} %Better spacing.
\usepackage[compact]{titlesec} %Custom sectioning. 'compact' shrinks all the whitespace around section headings.
\usepackage[font=small,labelfont=bf,labelsep=period]{caption} %Custom captions.
\usepackage{xcolor} %Colors.
\usepackage{multirow} %Cells that span multiples columns.
\usepackage{graphicx,eso-pic,lipsum,transparent, watermark}
\usepackage{textcomp} %Copyright and registered symbols.
\usepackage{booktabs} %Better tables.
\usepackage{xifthen} %IF/ELSE commands
%\usepackage{cuted} %Span figures and equations onto two columns.
\usepackage{enumitem}
	\setlist{noitemsep} % Reduce lists' line spacing.
% Other packages
\usepackage{amsthm, amscd, amsfonts, amssymb}
%\usepackage [displaymath, mathlines]{lineno}
\usepackage{hyperref}
\usepackage[table]{xcolor}
\usepackage{comment}
\usepackage{mfirstuc}
\hypersetup{colorlinks, linkcolor=black, urlcolor=black, citecolor=blue}
\definecolor{tablebg}{RGB}{220, 230, 242}
\definecolor{title}{RGB}{0, 122, 192}
\definecolor{abstract}{RGB}{234, 234, 234}
% New paragraphs will not be indented
\setlength{\parindent}{0pt}

% Gap between columns
\setlength{\columnsep}{0.5cm}

% No date
\date{}

\newcommand{\saucisJN}{SAKARYA UNIVERSITY JOURNAL OF COMPUTER AND}
\newcommand{\saucisJNn}{INFORMATION SCIENCES}
\newcommand{\saucisJI}{sau.png}
\newcommand{\saucisISSN}{{e-ISSN: 2636-8129}}
\newcommand{\saucisJS} {\href{http://saucis.sakarya.edu.tr/}{\textcolor{blue}{http://saucis.sakarya.edu.tr/}}}
\newcommand{\saucisDoi}{\href{https://doi.org/10.35377/saucis...\dergiparkID}{10.35377/saucis...\dergiparkID}}
\newcommand{\saucisJD}{Research Article}
\newcommand{\saucisP}{Publisher: Sakarya University}
\newcommand{\saucisJNb}{\textit{Sakarya University Journal of Computer and Information Sciences}~\vo ~ (\n) \y, ~\p }
\newcommand{\saucisC}{
\textbf{Cite as:} A. Yıldız, and F. Bozkurt, \makefirstuc{\MakeLowercase{"\THETITLE}"}, \saucisJNb. doi: \saucisDoi \\}
\newcommand{\saucisWarn}{\textcolor{red}{\it \textbf{Please keep only one of the types above and delete the others, including this phrase!}}}
\newcommand{\saucisAbstract}[1]{
\long\gdef\absText{\fontsize{9pt}{10.8pt}\selectfont#1}
}
\newcommand{\saucisKeywords}[1]{
\long\gdef\listKeywords{\fontsize{9pt}{9.6pt}\selectfont#1}
}
\newcommand{\saucisreceived}[1]{
\long\gdef\rec{\fontsize{8pt}{9.6pt}\selectfont#1}
}
\newcommand{\saucisrevised}[1]{
\long\gdef\rev{\fontsize{8pt}{9.6pt}\selectfont#1}
}
\newcommand{\saucisaccepted}[1]{
\long\gdef\acc{\fontsize{8pt}{9.6pt}\selectfont#1}
}
\newcommand{\saucisonline}[1]{
\long\gdef\onl{\fontsize{8pt}{9.6pt}\selectfont#1}
}

\gdef\rec{}
\gdef\rev{}
\gdef\acc{}
\gdef\onl{}

\newcommand{\saucisAuthors}{Authors}
\newcommand{\saucisCCC}{
\raisebox{-.4\height}{\includegraphics[width=0.65in,keepaspectratio]{cc.png}}}
\newcommand{\startsAtpage}[1]{\setcounter{page}{#1}}
\titleformat{\section}[block]%
{\normalfont\fontsize{10}{14.4}\bfseries}{\thesection.}{0.4em}%
{\normalfont\fontsize{10}{14.4}\bfseries\selectfont}

\titlespacing{\section}{0pt}{3pt}{3pt}
% Subsection
\titleformat{\subsection}[block]%
{\normalfont\fontsize{10}{12}\bfseries}{\thesubsection.}{0.4em}%
{\normalfont\fontsize{10}{12}\bfseries\selectfont}
\titlespacing{\subsection}{0pt}{3pt}{3pt}
% Subsubsection
\titleformat{\subsubsection}[block]%
{\normalfont\fontsize{9}{10.8}\bfseries}{\thesubsubsection.}{0.4em}%
{\normalfont\fontsize{9}{10.8}\bfseries\selectfont}
\titlespacing{\subsubsection}{0pt}{3pt}{3pt}

%-----------------------------------------------------------------
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Table columns
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\usepackage{array}
\newcolumntype{L}[1]{>{\raggedright\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{C}[1]{>{\centering\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{R}[1]{>{\raggedleft\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}

%-----------------------------------------------------------------
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Headings' styles
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\fancypagestyle{firstpage}{

    \fancyhf{}
    \renewcommand{\headrulewidth}{0pt}
	\renewcommand{\footrulewidth}{0.5pt}
	\setlength{\headsep}{-0.71in}
    %\renewcommand{\skip\footins{2cm}}
   %\renewcommand{\footnoterule}{\vspace{-8cm}}
	\fancyfoot[L]{%
    
           \saucisC% Cite as
           \vspace{0.5cm}
          	\saucisCCC \selectfont\fontsize{6pt}{9.6pt} This work is licensed under Creative Commons Attribution-NonCommercial 4.0 International License
}
}

\fancypagestyle{followingpage}{

	\fancyhf{} % clear all six fields 	
	\fancyhead[LE,LO]{\fontsize{8pt}{9.6pt}\selectfont{\saucisAuthors\hfill\saucisJNb}}
	%\renewcommand{\headrulewidth}{0.5pt}
     \renewcommand{\footrulewidth}{0.5pt}
       \fancyfoot[RE,RO]{\fontsize{8pt}{9.6pt}\selectfont\thepage}
}
% Default style
\pagestyle{followingpage}
% First page style
\AtBeginDocument{\thispagestyle{firstpage}}


%-----------------------------------------------------------------
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Customizations for authors' affiliation.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\renewcommand\Authfont{\bfseries}
\renewcommand\Affilfont{\normalfont\fontsize{9pt}{10.8pt}}
\renewcommand\Authands{,}
%-----------------------------------------------------------------
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Special gray cell for Journal Header.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\definecolor{gray}{HTML}{FBF2EF}
\newcommand{\specialcell}[2][c]{%

	\cellcolor{tablebg}
	\begin{tabular}{c}
	#2
	\end{tabular}
}

%-----------------------------------------------------------------
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Group headers and abstract in one column.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\def\maketitle{
  \if@twocolumn
    \twocolumn[\spcMaketitle]
  \else
    \spcMaketitle
  \fi
}

%-----------------------------------------------------------------
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Group headers and abstract in one column.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% All equations must be intirely aligned to the left.
\setlength{\mathindent}{1cm}

%-----------------------------------------------------------------
% Reduce line spacing and font for the bibliography.
\let\OLDthebibliography\thebibliography
\renewcommand\thebibliography[1]{
  \OLDthebibliography{#1}
  \fontsize{8}{0}\selectfont
  \setlength{\parskip}{0pt}
  \setlength{\itemsep}{0pt plus 1ex}
}

%\setcounter{page}{0}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% First page header, author, abstract and keywords.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Thicker line
\newcommand{\thickhline}{%
     {\ifnum 0=`}\fi \color{title}\hrule height 0.4em
    \futurelet \reserved@a \@xhline
}
% Thicker line
\newcommand{\thickhlinenew}{%
    {\ifnum 0=`}\fi \color{title}\hrule height 0.01em
    \futurelet \reserved@a \@xhline
}

% Cell spacing
\renewcommand{\arraystretch}{1}% Tighter

\newsavebox{\cellbox}
\newlength{\cellheight}

% The header
\def\spcMaketitle{
\vspace*{2cm}
        \thickhlinenew
         \vspace*{0.1cm}
	%	\begin{center}
%{\fontsize{8pt}{9.6pt} \it \saucisJNb}{\fontsize{8pt}{9.6pt} \it \saucisDoi}
		% @{} removes the cell padding.
		\begin{tabular}{@{}C{0.8in}C{5in}C{0.8in}@{}}

		 \includegraphics[width=0.78in,keepaspectratio]{logo} &	
        \specialcell{ 
			{\fontsize{13pt}{9pt} \bf\saucisJN}\\
            {\fontsize{13pt}{9pt} \bf\saucisJNn}\\
            {\fontsize{8pt}{9.6pt}  \saucisJS}\\\\
            }   
            \raggedright\saucisISSN  \hfill Vol. \vo, No.\n, \p, \y\\
            \saucisP \hfill DOI:10.35377/saucis...\dergiparkID
    		 & 
		\includegraphics[width=0.7in,keepaspectratio]{\saucisJI}
 		\end{tabular}
         \vspace*{0.1cm}
        \thickhline
        \begin{center}
             \specialcell{
    		{\fontsize{9pt}{9.6pt}  {\saucisJD}}}
         \end{center}
  \thickhlinenew
		% TITLE
		\vspace*{1.0cm}
		{\linespread{1.1}\fontsize{22pt}{21.6pt}  \raggedright \color{title} \selectfont\bf \@title\par}%
		% LIST OF AUTHORS
		\vspace*{0.5cm}
		{\raggedright\fontsize{10pt}{12pt} \@author}				
	%	\end{center}	
		\vspace*{0.3cm}	
        
% ABSTRACT===========================================

\setbox\cellbox=\vbox{%
\hsize=12.7cm
  \strut % ensures proper baseline alignment
    {\fontsize{10pt}{12pt}\textbf{Abstract}\newline}
        \absText
        {\newline\newline\fontsize{9pt}{10.8pt}\textbf{Keywords:}}
		\listKeywords
}
\setlength{\cellheight}{\dimexpr\ht\cellbox + \dp\cellbox\relax}

\thickhlinenew

\vspace*{0.1cm}

%\begin{table*}[h]
\centering
\begin{tabular}{p{4.5cm} p{12.7cm}}
\begin{minipage}[t][\the\cellheight][t]{0.45\textwidth}

{\fontsize{8pt}{8pt}\selectfont{*Corresponding author:\newline\corresAuthoremail}}

\vfill

{\fontsize{8pt}{10.8pt}\selectfont\textbf{Article History:}}\par
{\fontsize{8pt}{10.8pt}\selectfont Received: \rec}\par
{\fontsize{8pt}{10.8pt}\selectfont Revised: \rev}\par
{\fontsize{8pt}{10.8pt}\selectfont Accepted: \acc}\par
{\fontsize{8pt}{10.8pt}\selectfont Published Online: \onl}\par

\thiswatermark{\put(27,-380){\transparent{0.20}\includegraphics[width=1.in,keepaspectratio]{sau.png}}} 
\end{minipage}
                &
        \cellcolor{abstract}{\fontsize{10pt}{12pt}\textbf{Abstract}\newline}
        \absText
        {\newline\newline\fontsize{9pt}{10.8pt}\textbf{Keywords:}}
		\listKeywords
\end{tabular}

%\end{table*}
  \vspace*{0.1cm}    
  \thickhlinenew
   \vspace*{0.5cm}  
}
%-----------------------------------------------------------------
\endinput