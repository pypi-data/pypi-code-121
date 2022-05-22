from typing import List, Optional

from quickstats.utils.root_utils import declare_expression

ROOT_MACROS = \
{
    "TH1Utils":
    """
    namespace TH1Utils {
        template<typename T>
        std::vector<T> GetBinErrorArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinError(bin_index));
            return result;
        }

        template<typename T>
        std::vector<T> GetBinErrorUpArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinErrorUp(bin_index));
            return result;
        }

        template<typename T>
        std::vector<T> GetBinErrorLowArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinErrorLow(bin_index));
            return result;
        }

        template<typename T>
        std::vector<T> GetBinCenterArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinCenter(bin_index));
            return result;
        }

        template<typename T>
        std::vector<T> GetBinContentArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinContent(bin_index));
            return result;
        }
      
        template<typename T>
        std::vector<T> GetBinWidthArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinWidth(bin_index));
            return result;
        }

        template<typename T>
        std::vector<T> GetBinLowEdgeArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = h->GetNbinsX();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(h->GetBinLowEdge(bin_index));
            return result;
        }    
    }; 
    """,
    "TAxisUtils": 
    """
    namespace TAxisUtils{
        template<typename T>
        std::vector<T> GetBinLowEdgeArray(TAxis* ax, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = ax->GetNbins();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(ax->GetBinLowEdge(bin_index));
            return result;
        }
        template<typename T>
        std::vector<T> GetBinCenterArray(TAxis* ax, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = ax->GetNbins();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(ax->GetBinCenter(bin_index));
            return result;
        }
        template<typename T>
        std::vector<T> GetBinWidthArray(TAxis* ax, const size_t &underflow_bin=0, const size_t & overflow_bin=0)
        {
            const size_t n_bin = ax->GetNbins();
            std::vector<T> result;
            result.reserve(n_bin);
            const size_t bin_min = 1 - underflow_bin;
            const size_t bin_max = n_bin + overflow_bin;
            for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)
                result.push_back(ax->GetBinWidth(bin_index));
            return result;
        }
    };
    """,    
    "THistUtils": 
    """
    namespace THistUtils{
        template<typename T>
        std::vector<double> GetPoissonError(const std::vector<T> data){
            Double_t ym, yp;
            auto inst = RooHistError::instance();
            const int data_size = data.size();
            std::vector<double> result(2*data_size);
            for (size_t i = 0; i < data_size; i++){
                inst.getPoissonInterval(Int_t(data[i] + 0.5), ym, yp, 1);
                result[i] = data[i] - ym;
                result[data_size + i] = yp - data[i];
            }
            return result;
        }
    };
    """,
    "RFUtils":
    """
    namespace RFUtils{
        struct DatasetStruct {
          std::vector<double> observable_values;
          std::vector<double> weights;
          std::vector<std::string> category_labels;
          std::vector<int> category_index;
          DatasetStruct(const size_t &n_entries, const size_t &n_obs){
              observable_values = std::vector<double>(n_obs * n_entries);
              weights = std::vector<double>(n_entries);
              category_labels = std::vector<std::string>(n_entries);
              category_index = std::vector<int>(n_entries);
          }
        } ;
        
        DatasetStruct ExtractCategoryData(const RooAbsData* dataset, const RooArgSet* observables, const RooCategory* cat){
            const size_t n_entries = dataset->numEntries();
            const size_t n_obs = observables->size();
            DatasetStruct result(n_entries, n_obs);
            TIterator* iter(observables->createIterator());
            RooRealVar* obs;
            for (size_t i = 0; i < n_entries; i++){
                dataset->get(i);
                for (size_t j = 0; j < n_obs; j++)
                    result.observable_values[i + j * n_entries] = ((RooRealVar*)(*observables)[j])->getVal();
                result.weights[i] = dataset->weight();
                result.category_labels[i] = cat->getLabel();
                result.category_index[i] = cat->getIndex();
            }
            return result;
        }
        
        DatasetStruct ExtractData(const RooAbsData* dataset, const RooArgSet* observables){
            const size_t n_entries = dataset->numEntries();
            const size_t n_obs = observables->size();
            DatasetStruct result(n_entries, n_obs);
            TIterator* iter(observables->createIterator());
            RooRealVar* obs;
            for (size_t i = 0; i < n_entries; i++){
                dataset->get(i);
                for (size_t j = 0; j < n_obs; j++)
                    result.observable_values[i + j * n_entries] = ((RooRealVar*)(*observables)[j])->getVal();
                result.weights[i] = dataset->weight();
            }
            return result;
        }
        
         void CopyData(const RooAbsData* source, RooAbsData* target, const RooRealVar* source_var,
                       RooRealVar* target_var, RooRealVar* weight){
             for (size_t i = 0; i < source->numEntries(); i++){
                 source->get(i);
                 double weight_val = source->weight();
                 weight->setVal(weight_val);
                 target_var->setVal(source_var->getVal());
                 target->add(RooArgSet(*target_var, *weight), weight_val);
             }
        }
        
        struct RooArgSetInfo {
          std::vector<std::string> class_names;
          std::vector<std::string> names;
          RooArgSetInfo(const RooArgSet* argset){
            const size_t n_obj = argset->size();
            this->class_names = std::vector<std::string>(n_obj);
            this->names = std::vector<std::string>(n_obj);
            for (size_t i = 0; i < n_obj; i++){
                this->class_names[i] = ((TObject*)(*argset)[i])->ClassName();
                this->class_names[i] = ((TObject*)(*argset)[i])->GetName();
            }
          }
        } ;
    };
    """
}

def load_macro(macro_name:str):
    expression = ROOT_MACROS.get(macro_name, None)
    if expression is None:
        raise ValueError(f"`{macro_name}` is not a built-in quickstats macro."
                         " Available macros are: {}".format(",".join(list(ROOT_MACROS))))
    declare_expression(expression, macro_name)

def load_macros(macro_names:Optional[List[str]]=None):
    if macro_names is None:
        macro_names = list(ROOT_MACROS)
    for macro_name in macro_names:
        load_macro(macro_name)