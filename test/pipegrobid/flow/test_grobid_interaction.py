import pytest, os, requests
from pipegrobid.flow.grobid_interaction import list_pdfs, write_xml


# list_pdfs tests

def test_list_pdfs_empy(tmp_path):
    """
    Validación función list_pdfs(dirs_pdfs): directorio pdfs vacio
    """
    tmp_pdfs = os.path.join(tmp_path,"pdfs")
    os.makedirs(tmp_pdfs)
    
    pdfs = []
    assert list_pdfs(tmp_pdfs) == pdfs
    
    
def test_list_pdfs_not_empy(tmp_path):
    """
    Validación función list_pdfs(dirs_pdfs): directorio pdfs con .pdfs
    """
    tmp_pdfs = tmp_path/ "pdfs"
    os.makedirs(tmp_pdfs)
    dir_pdf1 = tmp_pdfs / "test1.pdf"
    dir_pdf2 = tmp_pdfs / "test2.pdf"
    dir_pdf1.touch()
    dir_pdf2.touch()
    
    pdfs = []
    pdfs.append(str(dir_pdf1))
    pdfs.append(str(dir_pdf2))
    
    assert sorted(list_pdfs(tmp_pdfs)) == sorted(pdfs)
    
    
    
    
def test_list_pdfs_more_file_types(tmp_path):
    """
    Validación función list_pdfs(dirs_pdfs): solo coge pdfs del dir
    """
    tmp_pdfs = tmp_path/ "pdfs"
    os.makedirs(tmp_pdfs)
    dir_pdf1 = tmp_pdfs / "test1.pdf"
    dir_txt1 = tmp_pdfs / "test2.txt"
    dir_pdf1.touch()
    dir_txt1.touch()
        
    pdfs = []
    pdfs.append(str(dir_pdf1))
        
    assert sorted(list_pdfs(tmp_pdfs)) == sorted(pdfs)
    
        
        
        
        
        

# test para write_xml

def test_write_xml_response_code_not_200(tmp_path):
    """
    Validación función write_xml(response, dir_xmls, i): cod de respuesta != 200
    """

    response = requests.Response()
    response.status_code = 404

    write_xml(response, str(tmp_path), 0)

    assert list(tmp_path.iterdir()) == []




def test_write_xml_response_code_200(tmp_path):
    """
    Validación función write_xml(response, dir_xmls, i): cod de respuesta == 200
    """

    response = requests.Response()
    response.status_code = 200
    response._content = b"<xml></xml>"

    write_xml(response, str(tmp_path), 0)

    created_file = tmp_path / "paper01.tei.xml"

    assert created_file.exists()
    assert created_file.is_file()


    
    
def test_write_xml_validate_xml(tmp_path):
    """
    Validación función write_xml(response, dir_xmls, i): se generan bien los xml (nombre y contenido)
    """

    xml_content = "<tei><title>Test</title></tei>"

    response = requests.Response()
    response.status_code = 200
    response._content = xml_content.encode("utf-8")

    write_xml(response, str(tmp_path), 2)

    created_file = tmp_path / "paper03.tei.xml"

    assert created_file.exists()
    assert created_file.read_text(encoding="utf-8") == xml_content